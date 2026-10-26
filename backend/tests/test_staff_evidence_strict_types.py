from datetime import datetime,timezone
import pytest
from app.staff_evidence_provider import VerifiedStaffEvidence,check_staff_with_provider

class Verifier:
 issuer="https://auth.ithute.example"
 def verify(self,token):return {"sub":"staff-1"}

class Provider:
 def __init__(self,value):self.value=value
 def get_verified_evidence(self,issuer,subject):return self.value

@pytest.mark.parametrize("bad",[
 VerifiedStaffEvidence("staff-1","true",True,True,True,"https://auth.ithute.example",datetime.now(timezone.utc),"lfm"),
 VerifiedStaffEvidence("staff-1",True,1,True,True,"https://auth.ithute.example",datetime.now(timezone.utc),"lfm"),
 VerifiedStaffEvidence("staff-1",True,True,"yes",True,"https://auth.ithute.example",datetime.now(timezone.utc),"lfm"),
 VerifiedStaffEvidence("staff-1",True,True,True,"true","https://auth.ithute.example",datetime.now(timezone.utc),"lfm"),
 VerifiedStaffEvidence("staff-1",True,True,True,True,"https://auth.ithute.example","2026-10-26","lfm"),
 VerifiedStaffEvidence("staff-1",True,True,True,True,"https://auth.ithute.example",datetime.now(),"lfm"),
])
def test_untyped_or_untrusted_evidence_is_denied(bad):
 with pytest.raises(PermissionError):
  check_staff_with_provider("token",Verifier(),Provider(bad),
   gateway_deployed=True,security_approved=True,expected_organization="lfm")
