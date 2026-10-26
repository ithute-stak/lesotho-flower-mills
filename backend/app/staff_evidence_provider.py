"""Fail-closed server-owned staff membership evidence adapter.

No HTTP request body or bearer-token claim can self-assert active membership.
An approved provider implementation must supply the callable after deployment.
"""
from dataclasses import dataclass
from typing import Protocol
from .staff_identity_gate import StaffAttestation,verify_staff_access

@dataclass(frozen=True)
class VerifiedStaffEvidence:
 subject:str
 active:bool
 member:bool
 mfa:bool
 session_active:bool

class TrustedStaffEvidenceProvider(Protocol):
 def get_verified_evidence(self,issuer:str,subject:str)->VerifiedStaffEvidence: ...

def check_staff_with_provider(token,verifier,provider:TrustedStaffEvidenceProvider|None,
                              *,gateway_deployed=False,security_approved=False):
 if provider is None:
  raise PermissionError("No approved identity evidence provider configured")
 claims=verifier.verify(token)
 evidence=provider.get_verified_evidence(verifier.issuer,claims["sub"])
 if evidence.subject!=claims["sub"]:
  raise PermissionError("Staff evidence subject mismatch")
 attestation=StaffAttestation(subject_active=evidence.active,
   membership_current=evidence.member,mfa_verified=evidence.mfa,
   session_not_revoked=evidence.session_active,
   gateway_deployed=gateway_deployed,security_approved=security_approved)
 _,decision=verify_staff_access(token,verifier,attestation)
 if not decision.allowed:
  raise PermissionError("Staff gateway authorization incomplete")
 return claims
