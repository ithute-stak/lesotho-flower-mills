import pytest
from app.staff_evidence_provider import VerifiedStaffEvidence,check_staff_with_provider

class Verifier:
 issuer="https://auth.ithute.example"
 def verify(self,token):
  if token!="valid":raise ValueError("bad token")
  return {"sub":"staff-1"}

class Provider:
 def __init__(self,evidence):self.evidence=evidence
 def get_verified_evidence(self,issuer,subject):
  assert issuer=="https://auth.ithute.example"
  return self.evidence

GOOD=VerifiedStaffEvidence("staff-1",True,True,True,True)

def test_missing_provider_denied():
 with pytest.raises(PermissionError):
  check_staff_with_provider("valid",Verifier(),None,gateway_deployed=True,security_approved=True)

def test_full_server_evidence_allows_only_with_approval():
 assert check_staff_with_provider("valid",Verifier(),Provider(GOOD),
  gateway_deployed=True,security_approved=True)["sub"]=="staff-1"
 with pytest.raises(PermissionError):
  check_staff_with_provider("valid",Verifier(),Provider(GOOD))

@pytest.mark.parametrize("evidence",[
 VerifiedStaffEvidence("other",True,True,True,True),
 VerifiedStaffEvidence("staff-1",False,True,True,True),
 VerifiedStaffEvidence("staff-1",True,False,True,True),
 VerifiedStaffEvidence("staff-1",True,True,False,True),
 VerifiedStaffEvidence("staff-1",True,True,True,False),
])
def test_invalid_or_wrong_subject_evidence_denied(evidence):
 with pytest.raises(PermissionError):
  check_staff_with_provider("valid",Verifier(),Provider(evidence),
   gateway_deployed=True,security_approved=True)

def test_invalid_token_denied_before_provider():
 with pytest.raises(ValueError):
  check_staff_with_provider("invalid",Verifier(),Provider(GOOD),
   gateway_deployed=True,security_approved=True)
