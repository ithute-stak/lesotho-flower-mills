import pytest
from fastapi import HTTPException
from app.staff_attestation_policy import validate_attestation_match

def test_matching_active_identity_is_eligible_for_future_attestation():
 validate_attestation_match(link_issuer="https://auth.example",
  link_subject="central-123",verified_issuer="https://auth.example",
  verified_subject="central-123",central_session_active=True)

@pytest.mark.parametrize("issuer,subject,active",[
 ("https://wrong.example","central-123",True),
 ("https://auth.example","different-user",True),
 ("https://auth.example","central-123",False),
])
def test_mismatch_or_revoked_session_fails_closed(issuer,subject,active):
 with pytest.raises(HTTPException) as exc:
  validate_attestation_match(link_issuer="https://auth.example",
   link_subject="central-123",verified_issuer=issuer,
   verified_subject=subject,central_session_active=active)
 assert exc.value.status_code==403
