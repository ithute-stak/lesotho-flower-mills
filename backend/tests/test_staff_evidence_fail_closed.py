import pytest
from app.staff_evidence_provider import check_staff_with_provider

class Verifier:
 issuer="https://auth.ithute.example"
 def verify(self,token):
  return {"sub":"staff-1"}

class BrokenProvider:
 def get_verified_evidence(self,issuer,subject):
  raise TimeoutError("provider timeout")

class MalformedProvider:
 def get_verified_evidence(self,issuer,subject):
  return {"subject":subject,"active":True}

def test_staff_provider_outage_is_access_denied():
 with pytest.raises(PermissionError,match="unavailable"):
  check_staff_with_provider("signed",Verifier(),BrokenProvider(),
   gateway_deployed=True,security_approved=True,expected_organization="lfm")

def test_untyped_identity_evidence_is_denied():
 with pytest.raises(PermissionError,match="format"):
  check_staff_with_provider("signed",Verifier(),MalformedProvider(),
   gateway_deployed=True,security_approved=True,expected_organization="lfm")

def test_missing_verified_subject_is_denied():
 class NoSubject(Verifier):
  def verify(self,token):return {"sub":""}
 with pytest.raises(PermissionError):
  check_staff_with_provider("signed",NoSubject(),BrokenProvider(),
   gateway_deployed=True,security_approved=True,expected_organization="lfm")
