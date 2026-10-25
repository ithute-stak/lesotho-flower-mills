"""Persist draft order totals; final approval awaits approved tax policy.

No staff-supplied tax rate may become a payable invoice by this endpoint.
"""
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
from .order_totals import calculate

router=APIRouter(prefix="/api/v1/admin/order-total-review",tags=["order-total-review"])

class DraftRequest(BaseModel):
 order_id:UUID
 discount:Decimal=Field(default=Decimal("0"),ge=0,decimal_places=2,max_digits=18)
 delivery_fee:Decimal=Field(default=Decimal("0"),ge=0,decimal_places=2,max_digits=18)
 tax_rate_bps:int=Field(ge=0,le=10000)
 delivery_taxable:bool=False
 policy_reference:str=Field(min_length=3,max_length=120)

@router.post("/drafts")
def save_draft(body:DraftRequest,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 order=db.execute(text("SELECT subtotal,status FROM sales.sales_orders WHERE id=:id FOR UPDATE"),{"id":body.order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 if order["status"]!="pending_payment":raise HTTPException(409,"Order is not awaiting payment")
 existing=db.execute(text("SELECT review_status FROM finance.order_totals WHERE sales_order_id=:id FOR UPDATE"),{"id":body.order_id}).mappings().first()
 if existing and existing["review_status"]=="approved":raise HTTPException(409,"Approved order total is immutable")
 try:values=calculate(Decimal(order["subtotal"]),body.discount,body.delivery_fee,body.tax_rate_bps,body.delivery_taxable)
 except ValueError as exc:raise HTTPException(422,str(exc))
 params={**values,"order":body.order_id,"rate":body.tax_rate_bps,"policy":body.policy_reference,"actor":identity["sub"]}
 db.execute(text("""INSERT INTO finance.order_totals(sales_order_id,subtotal,discount,delivery_fee,
 tax_rate_bps,taxable_base,tax_amount,total,currency,policy_reference,created_by,review_status)
 VALUES (:order,:subtotal,:discount,:delivery_fee,:rate,:taxable_base,:tax_amount,:total,'LSL',:policy,:actor,'draft')
 ON CONFLICT(sales_order_id) DO UPDATE SET subtotal=EXCLUDED.subtotal,discount=EXCLUDED.discount,
 delivery_fee=EXCLUDED.delivery_fee,tax_rate_bps=EXCLUDED.tax_rate_bps,
 taxable_base=EXCLUDED.taxable_base,tax_amount=EXCLUDED.tax_amount,total=EXCLUDED.total,
 policy_reference=EXCLUDED.policy_reference,created_by=EXCLUDED.created_by,review_status='draft'"""),params)
 db.commit()
 return {"order_id":str(body.order_id),"review_status":"draft","gross_total":str(values["total"]),
         "payable":False,"reason":"Tax, discount and freight policy have not been independently approved"}

@router.get("/orders/{order_id}")
def get_total(order_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT subtotal,discount,delivery_fee,tax_amount,total,currency,
 review_status,policy_reference,approved_at FROM finance.order_totals WHERE sales_order_id=:id"""),{"id":order_id}).mappings().first()
 if not row:raise HTTPException(404,"Order total not prepared")
 return dict(row)
