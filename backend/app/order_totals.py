"""Deterministic order totals; only drafts while tax/delivery policies await approval."""
from decimal import Decimal,ROUND_HALF_UP
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .finance_permissions import finance_read,finance_review
from .db import db_session

router=APIRouter(prefix="/api/v1/admin/orders",tags=["order-totals"])
CENT=Decimal("0.01")
def money(amount:Decimal)->Decimal:
 return amount.quantize(CENT,rounding=ROUND_HALF_UP)
def calculate(subtotal:Decimal,discount:Decimal,delivery_fee:Decimal,tax_rate_bps:int,delivery_taxable:bool=False)->dict:
 subtotal,discount,delivery_fee=map(money,(subtotal,discount,delivery_fee))
 if min(subtotal,discount,delivery_fee)<0 or discount>subtotal or not 0<=tax_rate_bps<=10000:
  raise ValueError("Invalid charges or tax rate")
 base=subtotal-discount+(delivery_fee if delivery_taxable else Decimal("0"))
 tax=money(base*Decimal(tax_rate_bps)/Decimal(10000))
 return {"subtotal":subtotal,"discount":discount,"delivery_fee":delivery_fee,
         "taxable_base":base,"tax_amount":tax,"total":money(subtotal-discount+delivery_fee+tax)}
class PreviewRequest(BaseModel):
 discount:Decimal=Field(default=Decimal("0"),ge=0,max_digits=18,decimal_places=2)
 delivery_fee:Decimal=Field(default=Decimal("0"),ge=0,max_digits=18,decimal_places=2)
 tax_rate_bps:int=Field(ge=0,le=10000)
 delivery_taxable:bool=False
 policy_reference:str=Field(min_length=3,max_length=120)
@router.post("/{order_id}/totals/preview")
def preview(order_id:UUID,body:PreviewRequest,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 row=db.execute(text("SELECT subtotal,status FROM sales.sales_orders WHERE id=:id"),{"id":order_id}).mappings().first()
 if not row:raise HTTPException(404,"Order not found")
 if row["status"]!="pending_payment":raise HTTPException(409,"Only unconfirmed orders can be previewed")
 try:breakdown=calculate(Decimal(row["subtotal"]),body.discount,body.delivery_fee,body.tax_rate_bps,body.delivery_taxable)
 except ValueError as e:raise HTTPException(422,str(e))
 return {"currency":"LSL","policy_reference":body.policy_reference,"charges":{k:str(v) for k,v in breakdown.items()},
         "approved":False,"payable":False,"note":"Preview only; official tax and delivery policy are not configured"}
