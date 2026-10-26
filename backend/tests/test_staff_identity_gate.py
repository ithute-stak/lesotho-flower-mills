import pytest
from app.staff_identity_gate import StaffAttestation,verify_staff_access

class StubVerifier:
 def verify(self,token):
  if token!="valid":
   raise ValueError("Invalid token")
  return {"sub":"trusted-staff"}

def test_missing_staff_attestations_deny_by_default():
 claims,decision=verify_staff_access("valid",StubVerifier(),StaffAttestation())
 assert claims["sub"]=="trusted-staff"
 assert not decision.allowed

@pytest.mark.parametrize("missing",[
 "subject_active","membership_current","mfa_verified","session_not_revoked",
 "gateway_deployed","security_approved"])
def test_any_missing_independent_attestation_denies(missing):
 flags={key:True for key in StaffAttestation.__dataclass_fields__}
 flags[missing]=False
 _,decision=verify_staff_access("valid",StubVerifier(),StaffAttestation(**flags))
 assert not decision.allowed

def test_full_attestation_policy_only_and_invalid_token_denied():
 flags={key:True for key in StaffAttestation.__dataclass_fields__}
 _,decision=verify_staff_access("valid",StubVerifier(),StaffAttestation(**flags))
 assert decision.allowed
 with pytest.raises(ValueError):
  verify_staff_access("invalid",StubVerifier(),StaffAttestation(**flags))
