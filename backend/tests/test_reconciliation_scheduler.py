from app.reconciliation_scheduler import run_once

def test_scheduler_disabled_by_default(monkeypatch):
 monkeypatch.delenv("LFM_RECONCILIATION_SCHEDULER_ENABLED",raising=False)
 assert run_once()=={"enabled":False,"reason":"scheduler_disabled"}

def test_worker_must_be_explicitly_enabled(monkeypatch):
 monkeypatch.setenv("LFM_RECONCILIATION_SCHEDULER_ENABLED","true")
 monkeypatch.delenv("LFM_ITHUTE_PAY_RECONCILIATION_ENABLED",raising=False)
 assert run_once()=={"enabled":False,"reason":"worker_disabled"}
