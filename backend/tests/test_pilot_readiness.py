from app.pilot_readiness import assess_pilot_readiness

def test_pilot_requires_independent_verification():
    result=assess_pilot_readiness()
    assert not result["demo_ready"]
    assert not result["external_pilot_ready"]
    assert not result["production_ready"]
    assert "settlement_verified" in result["missing_pilot_evidence"]
    assert "end_to_end_order_test" in result["missing_demo_evidence"]
