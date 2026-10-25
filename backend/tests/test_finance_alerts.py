from datetime import datetime,timezone,timedelta
from app.finance_alerts import calculate_alerts,AlertThresholds

def test_threshold_boundary():
 t=AlertThresholds(max_unresolved=3)
 assert calculate_alerts(None,2,t)==[]
 assert calculate_alerts(None,3,t)[0][0]=="unresolved_checkout_threshold"

def test_failed_worker_is_critical():
 alerts=calculate_alerts({"status":"failed","finished_at":None},0,AlertThresholds())
 assert alerts[0][1]=="critical"

def test_stale_worker():
 now=datetime.now(timezone.utc)
 alerts=calculate_alerts({"status":"completed","finished_at":now-timedelta(hours=3)},0,
                         AlertThresholds(stale_after_minutes=120),now)
 assert alerts[0][0]=="reconciliation_run_stale"
