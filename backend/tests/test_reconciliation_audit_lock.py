from decimal import Decimal
from app.checkout_recovery_worker import evaluate_session

def test_mismatched_reference_is_not_accepted():
 assert evaluate_session({"reference":"WRONG","amount":"430.00","currency":"LSL"},"LFM-1",Decimal("430.00"),"LSL")=="mismatch"

def test_remote_paid_status_is_only_an_observation():
 assert evaluate_session({"reference":"LFM-1","amount":"430.00","currency":"LSL","status":"paid"},"LFM-1",Decimal("430.00"),"LSL")=="observed"
