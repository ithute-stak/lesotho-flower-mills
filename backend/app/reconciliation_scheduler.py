"""One-shot guarded reconciliation entrypoint, intended for external hourly cron.

No timer runs in the API process. Requires explicit scheduler AND worker flags.
"""
import json
import os
from uuid import uuid4
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
  run_id=uuid4()
  with Session(engine) as db:
   db.execute(text("INSERT INTO finance.reconciliation_runs(id,status) VALUES (:id,'running')"),{"id":run_id})
   db.commit()
  try:
   with Session(engine) as db, httpx.Client(timeout=15.0) as client:
    result=reconcile_known_sessions(db,client,limit=25)
   status="skipped" if result.get("skipped") else "completed"
  except Exception:
   with Session(engine) as db:
    db.execute(text("""UPDATE finance.reconciliation_runs SET status='failed',finished_at=now()
    WHERE id=:id"""),{"id":run_id})
    db.commit()
   raise
  with Session(engine) as db:
   db.execute(text("""UPDATE finance.reconciliation_runs SET status=:status,
   checked=:checked,updated=:updated,finished_at=now() WHERE id=:id"""),
   {"id":run_id,"status":status,"checked":result.get("checked",0),
    "updated":result.get("updated",0)})
   db.commit()
  return result
 finally:
  engine.dispose()

def main()->None:
 result=run_once()
 print(json.dumps({"job":"lfm-payment-reconciliation","checked_at":datetime.now(timezone.utc).isoformat(),**result}))

if __name__=="__main__":
 main()
