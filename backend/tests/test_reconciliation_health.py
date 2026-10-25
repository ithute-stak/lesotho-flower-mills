from app.reconciliation_health import assess_health
def test_no_runs_is_unknown():
 assert assess_health(None,0)["status"]=="never_run"
def test_failed_run_alerts():
 assert assess_health({"status":"failed","started_at":None},2)["alert"] is True
def test_pending_items_trigger_attention():
 assert assess_health({"status":"completed","started_at":None},1)["alert"] is True
