from app.deployment_readiness import GATES,deployment_readiness

def test_deployment_never_self_certifies():
 review=deployment_readiness()
 assert review["deployment_approved"] is False
 assert review["external_pilot_approved"] is False
 assert len(review["gates"])==len(GATES)>=8
 assert len({g.code for g in GATES})==len(GATES)
 assert all(x["status"]=="unverified" and x["evidence_reference"] is None for x in review["gates"])

def test_internal_access_and_tls_are_required():
 codes={gate.code for gate in GATES}
 assert {"tls_certificate_verified","internal_portal_access_restricted",
         "backup_restore_verified","release_rollback_verified",
         "independent_security_review"}<=codes
