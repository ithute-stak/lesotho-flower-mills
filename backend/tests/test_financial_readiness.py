from app.financial_readiness import assess

def test_readiness_remains_blocked_even_with_approved_total():
 result=assess({"status":"pending_payment"},{"review_status":"approved","total":"2000.00","currency":"LSL"},
               {"status":"approved"})
 assert not result.ready
 assert "ithutepay_settlement_verification_pending" in result.blockers
def test_detects_amount_mismatch():
 result=assess({"status":"pending_payment"},{"review_status":"approved","total":"2000.00","currency":"LSL"},
               {"status":"approved"},{"amount":"1999.00","currency":"LSL"})
 assert "checkout_amount_mismatch" in result.blockers
def test_missing_approval():
 result=assess({"status":"pending_payment"},None,None)
 assert "gross_total_not_approved" in result.blockers
