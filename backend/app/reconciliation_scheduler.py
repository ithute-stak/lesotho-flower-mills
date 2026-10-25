"""One-shot guarded reconciliation entrypoint, intended for external hourly cron.

No timer runs in the API process. Requires explicit scheduler AND worker flags.
"""
import json
import os
from datetime import datetime,timezone
import httpx
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from .checkout_recovery_worker import reconcile_known_sessions

def run_once()->dict:
 if os.getenv("LFM_RECONCILIATION_SCHEDULER_ENABLED")!="true":
  return {"enabled":False,"reason":"scheduler_disabled"}
 if os.getenv("LFM_ITHUTE_PAY_RECONCILIATION_ENABLED")!="true":
  return {"enabled":False,"reason":"worker_disabled"}
 url=os.getenv("DATABASE_URL")
 if not url:
  raise RuntimeError("Database configuration required")
 engine=create_engine(url,pool_pre_ping=True)
 try:
  with Session(engine) as db, httpx.Client(timeout=15.0) as client:
   return reconcile_known_sessions(db,client,limit=25)
 finally:
  engine.dispose()

def main()->None:
 result=run_once()
 print(json.dumps({"job":"lfm-payment-reconciliation","checked_at":datetime.now(timezone.utc).isoformat(),**result}))

if __name__=="__main__":
 main()
