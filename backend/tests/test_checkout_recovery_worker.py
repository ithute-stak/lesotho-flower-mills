from decimal import Decimal
from app.checkout_recovery_worker import evaluate_session,reconcile_known_sessions

def test_remote_session_matches_order():
 assert evaluate_session({"reference":"LFM-1","amount":"430.00","currency":"LSL"},"LFM-1",Decimal("430.00"),"LSL")=="observed"

def test_remote_session_rejects_tampered_amount():
 assert evaluate_session({"reference":"LFM-1","amount":"431.00","currency":"LSL"},"LFM-1",Decimal("430.00"),"LSL")=="mismatch"

def test_remote_session_rejects_bad_fields():
 assert evaluate_session({"reference":"LFM-1","amount":"abc","currency":"LSL"},"LFM-1",Decimal("430.00"),"LSL")=="mismatch"

def test_worker_disabled_by_default(monkeypatch):
 monkeypatch.delenv("LFM_ITHUTE_PAY_RECONCILIATION_ENABLED",raising=False)
 assert reconcile_known_sessions(None,None)["enabled"] is False
