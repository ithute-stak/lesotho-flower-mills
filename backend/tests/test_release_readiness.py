from app.release_readiness import RELEASE_GATES,readiness_report

def test_release_is_not_self_approved_by_ci_or_claimed_evidence():
 report=readiness_report({g.code:"unverified-ci-ref" for g in RELEASE_GATES})
 assert report["production_ready"] is False
 assert report["external_pilot_approved"] is False
 assert len(report["unverified"])==len(RELEASE_GATES)==6
 assert all(g["claimed_reference"]=="unverified-ci-ref" for g in report["unverified"])

def test_required_signoffs_are_distinct_and_default_unverified():
 codes=[g.code for g in RELEASE_GATES]
 assert len(codes)==len(set(codes))
 assert {"ithute_auth","finance","fulfilment","security","operations","business"}==set(codes)
 assert all(g["claimed_reference"] is None for g in readiness_report()["unverified"])
