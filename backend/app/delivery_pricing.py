"""Safe read-only delivery tariff previews. Collection costs zero transport."""
from datetime import datetime,timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
from .order_totals import money

router=APIRouter(prefix="/api/v1/admin/delivery-pricing",tags=["delivery-pricing"])

def transport_fee(subtotal:Decimal,flat_fee:Decimal,free_minimum:Decimal|None=None)->Decimal:
 subtotal,flat_fee=money(subtotal),money(flat_fee)
 if subtotal<0 or flat_fee<0 or (free_minimum is not None and free_minimum<0):
  raise ValueError("Invalid transport tariff")
 return Decimal("0.00") if free_minimum is not None and subtotal>=free_minimum else flat_fee

class Preview(BaseModel):
 order_id:UUID
 fulfilment_method:Literal["collection","delivery"]
 zone_id:UUID|None=None

@router.post("/preview")
def preview_delivery(body:Preview,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 order=db.execute(text("SELECT subtotal,status FROM sales.sales_orders WHERE id=:id"),{"id":body.order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 if order["status"]!="pending_payment":raise HTTPException(409,"Only pending orders can be previewed")
 if body.fulfilment_method=="collection":
  if body.zone_id is not None:raise HTTPException(422,"Collection must not specify a delivery zone")
  return {"method":"collection","delivery_fee":"0.00","approved_order_total":False}
 if body.zone_id is None:raise HTTPException(422,"Delivery zone is required")
 tariffs=db.execute(text("""SELECT t.id,t.flat_fee,t.free_delivery_minimum,t.version
 FROM delivery.zones z JOIN delivery.tariffs t ON t.zone_id=z.id
 WHERE z.id=:zone AND z.active=true AND t.approved=true
 AND t.effective_from<=now() AND (t.effective_until IS NULL OR t.effective_until>now())
 ORDER BY t.version DESC LIMIT 2"""),{"zone":body.zone_id}).mappings().all()
 if len(tariffs)!=1:raise HTTPException(409,"Exactly one effective approved delivery tariff is required")
 tariff=tariffs[0]
 fee=transport_fee(Decimal(order["subtotal"]),Decimal(tariff["flat_fee"]),tariff["free_delivery_minimum"])
 return {"method":"delivery","zone_id":str(body.zone_id),"tariff_version":tariff["version"],
  "delivery_fee":str(fee),"approved_order_total":False}
