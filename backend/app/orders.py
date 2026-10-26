"""Controlled conversion of draft quotations into reserved, unpaid orders."""
from datetime import datetime,timezone
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
from .stock import reserve_quantity
from .finance_permissions import finance_admin

router=APIRouter(prefix="/api/v1/admin/orders",tags=["sales-orders"])

class CreateOrder(BaseModel):
    quotation_id: UUID
    warehouse_id: UUID

@router.post("",status_code=201)
def create_order(body:CreateOrder,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
    # Lock the quote to prevent two conversions of the same draft.
    quotation=db.execute(text("""SELECT id,customer_id,subtotal,status,expires_at
      FROM sales.quotations WHERE id=:id FOR UPDATE"""),{"id":body.quotation_id}).mappings().first()
    if not quotation:
        raise HTTPException(404,"Quotation not found")
    if quotation["status"]!="draft" or quotation["expires_at"]<=datetime.now(timezone.utc):
        raise HTTPException(409,"Quotation is not an active draft")
    existing=db.execute(text("SELECT id FROM sales.sales_orders WHERE quotation_id=:id"),{"id":body.quotation_id}).first()
    if existing:
        raise HTTPException(409,"Quotation was already converted")
    rows=db.execute(text("""SELECT id,product_id,quantity
      FROM sales.quotation_items WHERE quotation_id=:id ORDER BY product_id"""),
      {"id":body.quotation_id}).mappings().all()
    if not rows:
        raise HTTPException(422,"Quotation has no lines")
    for row in rows:
        if not reserve_quantity(db,body.warehouse_id,row["product_id"],row["quantity"]):
            db.rollback()
            raise HTTPException(409,"Insufficient available stock for one or more products")
    oid=uuid4()
    reference="LFM-ORD-"+datetime.now(timezone.utc).strftime("%Y%m%d")+"-"+str(oid)[:8].upper()
    db.execute(text("""INSERT INTO sales.sales_orders
      (id,order_number,quotation_id,customer_id,warehouse_id,status,subtotal)
      VALUES (:id,:number,:quote,:customer,:warehouse,'pending_payment',:subtotal)"""),
      {"id":oid,"number":reference,"quote":body.quotation_id,"customer":quotation["customer_id"],
       "warehouse":body.warehouse_id,"subtotal":quotation["subtotal"]})
    for row in rows:
        db.execute(text("""INSERT INTO inventory.stock_reservations
          (id,quotation_item_id,warehouse_id,product_id,quantity)
          VALUES (:id,:item,:warehouse,:product,:quantity)"""),
          {"id":uuid4(),"item":row["id"],"warehouse":body.warehouse_id,
           "product":row["product_id"],"quantity":row["quantity"]})
    db.commit()
    return {"id":str(oid),"order_number":reference,"status":"pending_payment",
            "stock_reserved":True,"payment_received":False}


@router.post("/{order_id}/cancel")
def cancel_unpaid_order(order_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
    """Release stock only for a pending, unpaid order, under row locks."""
    order=db.execute(text("""SELECT id,quotation_id,status FROM sales.sales_orders
      WHERE id=:id FOR UPDATE"""),{"id":order_id}).mappings().first()
    if not order:raise HTTPException(404,"Order not found")
    if order["status"]!="pending_payment":
        raise HTTPException(409,"Only pending-payment orders can be cancelled here")
    if db.execute(text("""SELECT 1 FROM fulfilment.pick_lists
      WHERE sales_order_id=:order LIMIT 1"""),{"order":order_id}).first():
        raise HTTPException(409,"Order already entered fulfilment")
    # An existing checkout represents possible external payment activity.
    # Without authoritative settlement/refund reconciliation, cancel none of it.
    if db.execute(text("""SELECT 1 FROM finance.checkout_sessions
      WHERE sales_order_id=:order LIMIT 1 FOR UPDATE"""),{"order":order_id}).first():
        raise HTTPException(409,"Checkout activity requires financial reconciliation before cancellation")
    reservations=db.execute(text("""SELECT sr.id,sr.warehouse_id,sr.product_id,sr.quantity
      FROM inventory.stock_reservations sr
      JOIN sales.quotation_items qi ON qi.id=sr.quotation_item_id
      WHERE qi.quotation_id=:quotation AND sr.status='active'
      ORDER BY sr.id FOR UPDATE OF sr"""),{"quotation":order["quotation_id"]}).mappings().all()
    for reservation in reservations:
        change=db.execute(text("""UPDATE inventory.stock_balances
          SET reserved=reserved-:qty
          WHERE warehouse_id=:warehouse AND product_id=:product AND reserved>=:qty"""),
          {"qty":reservation["quantity"],"warehouse":reservation["warehouse_id"],
           "product":reservation["product_id"]})
        if change.rowcount!=1:
            db.rollback()
            raise HTTPException(409,"Reservation balance mismatch; cancellation aborted")
        db.execute(text("""UPDATE inventory.stock_reservations SET status='released'
          WHERE id=:id AND status='active'"""),{"id":reservation["id"]})
    db.execute(text("""UPDATE sales.sales_orders SET status='cancelled'
      WHERE id=:id AND status='pending_payment'"""),{"id":order_id})
    db.execute(text("""INSERT INTO sales.order_cancellation_events
      (id,order_id,actor_subject,released_count)
      VALUES (:id,:order,:actor,:count)"""),
      {"id":uuid4(),"order":order_id,"actor":identity["sub"],"count":len(reservations)})
    db.commit()
    return {"id":str(order_id),"status":"cancelled","released_reservations":len(reservations)}
