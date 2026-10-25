"""Policy-bound draft totals. Never promotes orders to payable status."""
from decimal import Decimal
from uuid import UUID
from typing import Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
from .order_totals import calculate,money
from .delivery_pricing import transport_fee

router=APIRouter(prefix="/api/v1/admin/policy-order-totals",tags=["policy-order-totals"])

class PolicyDraft(BaseModel):
 order_id:UUID
 policy_id:UUID
 discount:Decimal=Field(default=Decimal("0"),ge=0,max_digits=18,decimal_places=2)
 method:Literal["collection","delivery"]
 zone_id:UUID|None=None

def discount_allowed(subtotal:Decimal,discount:Decimal,limit_bps:int)->bool:
 if subtotal<0 or discount<0 or not 0<=limit_bps<=10000:return False
 return money(discount)<=money(subtotal*Decimal(limit_bps)/Decimal(10000))

@router.post("/drafts",status_code=201)
def create_policy_draft(body:PolicyDraft,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 order=db.execute(text("SELECT subtotal,status FROM sales.sales_orders WHERE id=:id FOR UPDATE"),
  {"id":body.order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 if order["status"]!="pending_payment":raise HTTPException(409,"Order must await payment")
 policy=db.execute(text("""SELECT id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps
 FROM finance.financial_policies WHERE id=:id AND status='approved'
 AND effective_from<=now()"""),{"id":body.policy_id}).mappings().first()
 if not policy:raise HTTPException(409,"Approved effective financial policy required")
 subtotal=Decimal(order["subtotal"])
 if not discount_allowed(subtotal,body.discount,policy["max_discount_bps"]):
  raise HTTPException(422,"Discount exceeds approved financial policy")
 fee=Decimal("0")
 tariff_ref="collection"
 if body.method=="collection":
  if body.zone_id is not None:raise HTTPException(422,"Collection cannot specify zone")
 else:
  if body.zone_id is None:raise HTTPException(422,"Delivery requires zone")
  tariffs=db.execute(text("""SELECT t.id,t.version,t.flat_fee,t.free_delivery_minimum
 FROM delivery.tariffs t JOIN delivery.zones z ON z.id=t.zone_id
 WHERE t.zone_id=:zone AND z.active=true AND t.approved=true
 AND t.effective_from<=now() AND (t.effective_until IS NULL OR t.effective_until>now())
 LIMIT 2"""),{"zone":body.zone_id}).mappings().all()
  if len(tariffs)!=1:raise HTTPException(409,"Exactly one active approved tariff required")
  t=tariffs[0]
  fee=transport_fee(subtotal-body.discount,Decimal(t["flat_fee"]),t["free_delivery_minimum"])
  tariff_ref=str(t["id"])+":v"+str(t["version"])
 breakdown=calculate(subtotal,body.discount,fee,policy["tax_rate_bps"],policy["delivery_taxable"])
 existing=db.execute(text("SELECT review_status FROM finance.order_totals WHERE sales_order_id=:id FOR UPDATE"),
  {"id":body.order_id}).mappings().first()
 if existing and existing["review_status"]=="approved":raise HTTPException(409,"Approved total is immutable")
 reference=policy["code"]+":v"+str(policy["version"])+":"+str(policy["id"])+":"+tariff_ref
 values={**breakdown,"id":body.order_id,"rate":policy["tax_rate_bps"],
         "reference":reference[:120],"actor":identity["sub"]}
 db.execute(text("""INSERT INTO finance.order_totals
 (sales_order_id,subtotal,discount,delivery_fee,tax_rate_bps,taxable_base,tax_amount,total,
 currency,policy_reference,created_by,review_status)
 VALUES (:id,:subtotal,:discount,:delivery_fee,:rate,:taxable_base,:tax_amount,:total,
 'LSL',:reference,:actor,'draft')
 ON CONFLICT(sales_order_id) DO UPDATE SET
 subtotal=EXCLUDED.subtotal,discount=EXCLUDED.discount,delivery_fee=EXCLUDED.delivery_fee,
 tax_rate_bps=EXCLUDED.tax_rate_bps,taxable_base=EXCLUDED.taxable_base,
 tax_amount=EXCLUDED.tax_amount,total=EXCLUDED.total,
 policy_reference=EXCLUDED.policy_reference,created_by=EXCLUDED.created_by,
 review_status='draft'"""),values)
 db.commit()
 return {"order_id":str(body.order_id),"policy_id":str(body.policy_id),
   "method":body.method,"gross_total":str(breakdown["total"]),
   "review_status":"draft","payable":False}
