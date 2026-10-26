from itertools import product
from app.staff_gateway_policy import staff_gateway_decision

FIELDS=("issuer_verified","audience_verified","signature_verified","subject_active",
        "membership_current","mfa_verified","session_not_revoked",
        "gateway_deployed","security_approved")

def test_gateway_rejects_every_incomplete_combination():
 for values in product((False,True),repeat=len(FIELDS)):
  decision=staff_gateway_decision(**dict(zip(FIELDS,values)))
  assert decision.allowed is all(values)

def test_gateway_defaults_to_deny():
 assert not staff_gateway_decision().allowed

def test_public_gateway_stays_unrouted():
 from pathlib import Path
 caddy=(Path(__file__).resolve().parents[2]/"deploy/Caddyfile").read_text()
 for name in ("ADMIN","WAREHOUSE"):
  virtualhost=caddy.split("{$LFM_"+name+"_DOMAIN} {",1)[1].split("\n}",1)[0]
  assert 'respond "Internal portal access is not activated" 403' in virtualhost
  assert "reverse_proxy" not in virtualhost
