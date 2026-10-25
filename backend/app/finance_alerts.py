"""Deterministic finance health alerts; no unverified payment notifications."""
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session

@dataclass(frozen=True)
class AlertThresholds:
 max_unresolved:int=5
 stale_after_minutes:int=120

def calculate_alerts(latest,unresolved:int,thresholds:AlertThresholds,now=None):
 now=now or datetime.now(timezone.utc)
 alerts=[]
 if unresolved>=thresholds.max_unresolved and unresolved>0:
  alerts.append(("unresolved_checkout_threshold","warning",f"{unresolved} unresolved checkout attempts"))
 if latest is not None and latest["status"]=="failed":
  alerts.append(("reconciliation_run_failed","critical","Latest reconciliation run failed"))
 elif latest is not None and latest.get("finished_at") is not None:
  age=now-latest["finished_at"]
  if age>timedelta(minutes=thresholds.stale_after_minutes):
   alerts.append(("reconciliation_run_stale","warning","Latest completed reconciliation is stale"))
 return alerts

def persist_alerts(db:Session,alerts,period:str)->int:
 count=0
 for code,severity,details in alerts:
  db.execute(text("""INSERT INTO finance.operational_alerts
   (id,code,dedupe_key,severity,details) VALUES (:id,:code,:key,:severity,:details)
   ON CONFLICT(dedupe_key) DO NOTHING"""),
   {"id":uuid4(),"code":code,"key":f"{code}:{period}",
    "severity":severity,"details":details})
  count+=1
 db.commit()
 return count
