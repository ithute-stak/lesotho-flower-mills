"""Read-only operator health summary. A run is not proof of payment settlement."""
from datetime import datetime,timezone,timedelta
def assess_health(latest,unresolved:int,now=None)->dict:
 if latest is None:return {"status":"never_run","alert":True,"unresolved":unresolved}
 now=now or datetime.now(timezone.utc)
 status=latest["status"]
 started=latest.get("started_at")
 stale=bool(started and now-started>timedelta(hours=2))
 return {"status":"stale" if stale else status,
         "alert":status!="completed" or stale or unresolved>0,
         "unresolved":unresolved}
