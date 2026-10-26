from app.finance_security_assessment import GATES,finance_security_assessment

def test_finance_signoff_requires_independent_evidence():
 result=finance_security_assessment()
 assert result["approved"] is False
 assert result["external_pilot_allowed"] is False
 assert len(result["gates"])==len(GATES)>=9
 assert len({x["code"] for x in result["gates"]})==len(GATES)
 assert all(x["status"]=="unverified" and x["reviewed_by"] is None and x["evidence_reference"] is None for x in result["gates"])

def test_settlement_and_identity_are_mandatory():
 names={g.code for g in GATES}
 assert {"identity_attestation","payment_settlement","refund_reversal","independent_signoff"}<=names
