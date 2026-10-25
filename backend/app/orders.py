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
