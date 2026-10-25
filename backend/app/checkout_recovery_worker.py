"""Read-only IthutePay session reconciliation. NEVER initiate charges."""
import os
from decimal import Decimal,InvalidOperation
import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session
from .ithute_pay_adapter import IthutePayCheckoutAdapter

def evaluate_session(remote:dict,expected_reference:str,amount:Decimal,currency:str)->str:
 try:
  if remote.get("reference")!=expected_reference or remote.get("currency")!=currency or Decimal(str(remote.get("amount")))!=amount:
   return "mismatch"
 except (InvalidOperation,ValueError,TypeError):
  return "mismatch"
 return "observed"

def reconcile_known_sessions(db:Session,client:httpx.Client,*,limit:int=25)->dict:
 if os.getenv("LFM_ITHUTE_PAY_RECONCILIATION_ENABLED")!="true":
  return {"enabled":False,"checked":0,"updated":0}
 url=os.getenv("LFM_ITHUTE_PAY_API_URL","")
 key=os.getenv("LFM_ITHUTE_PAY_API_KEY","")
 if not url or not key:
  raise RuntimeError("IthutePay reconciliation credentials missing")
 adapter=IthutePayCheckoutAdapter(url,key,client)
 rows=db.execute(text("""SELECT a.id,a.provider_session_id,a.amount,a.currency,
 o.order_number FROM finance.checkout_attempts a
 JOIN sales.sales_orders o ON o.id=a.sales_order_id
 WHERE a.state IN ('created','reconciliation_required')
 AND a.provider_session_id IS NOT NULL
 ORDER BY a.updated_at ASC LIMIT :limit"""),{"limit":max(1,min(limit,100))}).mappings().all()
 checked=updated=0
 for row in rows:
  checked+=1
  try:
   remote=adapter.get_checkout(row["provider_session_id"])
   result=evaluate_session(remote,row["order_number"],Decimal(row["amount"]),row["currency"])
  except (httpx.HTTPError,ValueError,KeyError):
   continue
  if result!="observed":
   db.execute(text("""UPDATE finance.checkout_attempts
    SET state='reconciliation_required',updated_at=now() WHERE id=:id"""),{"id":row["id"]})
  else:
   # We ONLY record the remote observation. 'paid' is not settlement proof.
   db.execute(text("""UPDATE finance.checkout_sessions SET state=:state,last_checked_at=now()
    WHERE provider_session_id=:remote"""),
    {"state":str(remote.get("status","unknown"))[:30],"remote":row["provider_session_id"]})
  db.commit()
  updated+=1
 return {"enabled":True,"checked":checked,"updated":updated,
         "payment_verified":False,"orders_confirmed":0}
