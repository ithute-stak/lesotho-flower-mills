from datetime import datetime,timezone
from app.staff_evidence_provider import VerifiedStaffEvidence,check_staff_with_provider

class CountingVerifier:
 issuer="https://auth.ithute.example"
 def __init__(self):self.calls=0
 def verify(self,token):
  self.calls+=1
  if self.calls>1:raise AssertionError("Unexpected second JWT validation")
  return {"sub":"staff-one"}

class Evidence:
 def get_verified_evidence(self,issuer,subject):
  return VerifiedStaffEvidence(subject,True,True,True,True,issuer,datetime.now(timezone.utc),"lfm")

def test_staff_authorization_verifies_jwt_only_once():
 verifier=CountingVerifier()
 claims=check_staff_with_provider("valid",verifier,Evidence(),
  gateway_deployed=True,security_approved=True,expected_organization="lfm")
 assert claims["sub"]=="staff-one"
 assert verifier.calls==1
