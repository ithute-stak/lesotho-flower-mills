"""Staff-only, opt-in IthutePay checkout staging and status reconciliation.

Remote statuses are observations, not evidence of final settlement.
"""
import os
from decimal import Decimal
from uuid import UUID,uuid4
import httpx
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from .authorization import staff_identity
from .db import db_session
from .ithute_pay_adapter import CheckoutRequest,IthutePayCheckoutAdapter

router=APIRouter(prefix="/api/v1/admin/ithute-pay",tags=["ithute-pay"])

class CheckoutStart(BaseModel):
 order_id:UUID

def adapter(client:httpx.Client)->IthutePayCheckoutAdapter:
 if os.getenv("LFM_ITHUTE_PAY_CHECKOUT_ENABLED")!="true":
  raise HTTPException(503,"IthutePay checkout is not activated")
 url=os.getenv("LFM_ITHUTE_PAY_API_URL","")
 key=os.getenv("LFM_ITHUTE_PAY_API_KEY","")
 if not url or not key:raise HTTPException(503,"IthutePay configuration incomplete")
 try:return IthutePayCheckoutAdapter(url,key,client)
 except ValueError:raise HTTPException(503,"Invalid IthutePay configuration")

@router.post("/checkouts",status_code=201)
def start_checkout(body:CheckoutStart,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 # No customer-driven payments until quote taxes and delivery pricing are final.
 if os.getenv("LFM_ITHUTE_PAY_CHECKOUT_ENABLED")!="true":raise HTTPException(503,"Checkout disabled")
 order=db.execute(text("SELECT id,order_number,subtotal,status FROM sales.sales_orders WHERE id=:id FOR UPDATE"),
  {"id":body.order_id}).mappings().first()
 if not order:raise HTTPException(404,"Order not found")
 if order["status"]!="pending_payment":raise HTTPException(409,"Order not awaiting payment")
 approved=db.execute(text("""SELECT total,currency,review_status FROM finance.order_totals
 WHERE sales_order_id=:id FOR UPDATE"""),{"id":body.order_id}).mappings().first()
 if not approved or approved["review_status"]!="approved" or approved["currency"]!="LSL":
  raise HTTPException(409,"Independently approved gross order total required")
 if Decimal(approved["total"])<=0:raise HTTPException(422,"Invalid payable amount")
 # Persist an attempt BEFORE calling IthutePay. Unknown outcomes are never retried blindly.
 from sqlalchemy.exc import IntegrityError
 attempt=db.execute(text("""SELECT state,provider_session_id FROM finance.checkout_attempts
 WHERE sales_order_id=:id FOR UPDATE"""),{"id":body.order_id}).mappings().first()
 if attempt:
  raise HTTPException(409,"Checkout already initiated; reconcile the prior attempt before retrying")
 session_id=uuid4()
 idempotency_key="lfm-"+str(session_id)
 try:
  db.execute(text("""INSERT INTO finance.checkout_attempts
  (id,sales_order_id,idempotency_key,state,amount,currency,created_by)
  VALUES (:id,:order,:key,'initiating',:amount,'LSL',:actor)"""),
  {"id":session_id,"order":body.order_id,"key":idempotency_key,
   "amount":approved["total"],"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback()
  raise HTTPException(409,"Checkout attempt already exists; reconcile before retrying")
 try:
  with httpx.Client() as client:
   session=adapter(client).create_checkout(
    CheckoutRequest(order["order_number"],Decimal(approved["total"])),
    idempotency_key=idempotency_key)
 except (httpx.HTTPError,ValueError) as exc:
  db.execute(text("""UPDATE finance.checkout_attempts
  SET state='reconciliation_required',updated_at=now() WHERE id=:id"""),{"id":session_id})
  db.commit()
  raise HTTPException(502,"Payment initiation outcome uncertain; reconcile before retrying") from exc
 db.execute(text("""UPDATE finance.checkout_attempts
 SET state='created',provider_session_id=:remote,updated_at=now() WHERE id=:id"""),
 {"id":session_id,"remote":session["payment_session_id"]})
 db.execute(text("""INSERT INTO finance.checkout_sessions
 (id,sales_order_id,provider_session_id,idempotency_key,amount,currency,state,created_by)
 VALUES (:id,:order,:remote,:key,:amount,'LSL',:state,:actor)"""),
 {"id":session_id,"order":body.order_id,"remote":session["payment_session_id"],"key":idempotency_key,
  "amount":approved["total"],"state":session["status"],"actor":identity["sub"]})
 db.commit()
 return {"session_id":session["payment_session_id"],"checkout_url":session["checkout_url"],
         "status":session["status"],"order_confirmed":False}

@router.get("/orders/{order_id}/attempt")
def checkout_attempt(order_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT state,provider_session_id,created_at,updated_at
 FROM finance.checkout_attempts WHERE sales_order_id=:order"""),{"order":order_id}).mappings().first()
 if not row:raise HTTPException(404,"No checkout attempt found")
 return {"state":row["state"],"provider_session_id":row["provider_session_id"],
         "created_at":row["created_at"],"updated_at":row["updated_at"],
         "safe_to_retry":False}

@router.post("/checkouts/{session_id}/refresh")
def refresh_checkout(session_id:UUID,identity:dict=Depends(staff_identity),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT id,sales_order_id,provider_session_id,amount,currency,state
 FROM finance.checkout_sessions WHERE id=:id FOR UPDATE"""),{"id":session_id}).mappings().first()
 if not row:raise HTTPException(404,"Checkout session not found")
 try:
  with httpx.Client() as client:state=adapter(client).get_checkout(row["provider_session_id"])
 except (httpx.HTTPError,ValueError) as exc:
  db.rollback();raise HTTPException(502,"Payment status check failed") from exc
 order=db.execute(text("SELECT order_number FROM sales.sales_orders WHERE id=:id"),
  {"id":row["sales_order_id"]}).mappings().first()
 if not order or state.get("reference")!=order["order_number"] or state.get("currency")!=row["currency"] or Decimal(str(state.get("amount",0)))!=Decimal(row["amount"]):
  db.rollback();raise HTTPException(409,"Payment status does not match stored order")
 remote_status=str(state.get("status","unknown"))[:30]
 db.execute(text("""UPDATE finance.checkout_sessions SET state=:state,last_checked_at=now() WHERE id=:id"""),
  {"state":remote_status,"id":session_id})
 db.commit()
 return {"session_id":str(session_id),"observed_status":remote_status,"verified_settlement":False,"order_confirmed":False}
