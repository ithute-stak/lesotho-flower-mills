"""Payment records and fail-closed order authorisation.

Provider callbacks and credit-account verification are not yet connected.
Only trusted verified payment records may authorise cash orders.
"""
from decimal import Decimal
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .finance_permissions import finance_read,finance_review,finance_admin
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/finance",tags=["finance"])

class PaymentRecord(BaseModel):
    order_id:UUID
    provider:str=Field(min_length=2,max_length=60)
    provider_reference:str=Field(min_length=5,max_length=180)
    amount:Decimal=Field(gt=0,max_digits=18,decimal_places=2)

@router.post("/payments",status_code=201)
def record_payment(body:PaymentRecord,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
    # A staff-entered payment is UNVERIFIED: it cannot authorise stock release.
    order=db.execute(text("SELECT id FROM sales.sales_orders WHERE id=:id"),{"id":body.order_id}).first()
    if not order:raise HTTPException(404,"Order not found")
    pid=uuid4()
    from sqlalchemy.exc import IntegrityError
    try:
        db.execute(text("""INSERT INTO finance.payment_transactions
           (id,sales_order_id,provider,provider_reference,amount,verification_status)
           VALUES (:id,:order,:provider,:ref,:amount,'pending')"""),
           {"id":pid,"order":body.order_id,"provider":body.provider,
            "ref":body.provider_reference,"amount":body.amount})
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,"Payment reference already recorded")
    return {"id":str(pid),"verification_status":"pending","authorised":False}

@router.get("/orders/{order_id}/payments")
def order_payments(order_id:UUID,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
    rows=db.execute(text("""SELECT id,provider,provider_reference,amount,currency,verification_status,
      created_at,verified_at FROM finance.payment_transactions
      WHERE sales_order_id=:order ORDER BY created_at DESC"""),{"order":order_id}).mappings().all()
    return [dict(r) for r in rows]

@router.post("/orders/{order_id}/confirm-payment")
def confirm_paid_order(order_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
    order=db.execute(text("""SELECT id,status,subtotal FROM sales.sales_orders
       WHERE id=:id FOR UPDATE"""),{"id":order_id}).mappings().first()
    if not order:raise HTTPException(404,"Order not found")
    if order["status"]!="pending_payment":raise HTTPException(409,"Order is not awaiting payment")
    verified=db.execute(text("""SELECT COALESCE(SUM(amount),0) FROM finance.payment_transactions
      WHERE sales_order_id=:id AND verification_status='verified' AND currency='LSL'"""),
      {"id":order_id}).scalar_one()
    if Decimal(verified)<Decimal(order["subtotal"]):
        raise HTTPException(409,"Verified payments do not cover order subtotal")
    # In production the order total must include final approved taxes and delivery fees.
    # Until that commercial policy exists, do not permit real order confirmation.
    raise HTTPException(409,"Order confirmation is disabled until tax, delivery and settlement validation is implemented")
