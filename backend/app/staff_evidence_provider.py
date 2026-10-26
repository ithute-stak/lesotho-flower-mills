"""Fail-closed server-owned staff membership evidence adapter.

No HTTP request body or bearer-token claim can self-assert active membership.
An approved provider implementation must supply the callable after deployment.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from .staff_identity_gate import StaffAttestation,verify_staff_access

@dataclass(frozen=True)
class VerifiedStaffEvidence:
 subject:str
 active:bool
 member:bool
 mfa:bool
 session_active:bool
 issuer:str=""
 verified_at:datetime|None=None
 organization_id:str=""

class TrustedStaffEvidenceProvider(Protocol):
 def get_verified_evidence(self,issuer:str,subject:str)->VerifiedStaffEvidence: ...

def check_staff_with_provider(token,verifier,provider:TrustedStaffEvidenceProvider|None,
                              *,gateway_deployed=False,security_approved=False,
                              expected_organization:str="",max_evidence_age_seconds:int=120):
 if provider is None:
  raise PermissionError("No approved identity evidence provider configured")
 claims=verifier.verify(token)
 evidence=provider.get_verified_evidence(verifier.issuer,claims["sub"])
 if evidence.subject!=claims["sub"] or evidence.issuer!=verifier.issuer:
  raise PermissionError("Staff evidence issuer or subject mismatch")
 if not expected_organization or evidence.organization_id!=expected_organization:
  raise PermissionError("Staff organisation scope unverified")
 if not 1<=max_evidence_age_seconds<=300:
  raise PermissionError("Invalid staff evidence freshness policy")
 stamp=evidence.verified_at
 if stamp is None or stamp.tzinfo is None:
  raise PermissionError("Staff evidence freshness unavailable")
 age=(datetime.now(timezone.utc)-stamp).total_seconds()
 if age < -30 or age > max_evidence_age_seconds:
  raise PermissionError("Staff evidence expired or future dated")
 attestation=StaffAttestation(subject_active=evidence.active,
   membership_current=evidence.member,mfa_verified=evidence.mfa,
   session_not_revoked=evidence.session_active,
   gateway_deployed=gateway_deployed,security_approved=security_approved)
 _,decision=verify_staff_access(token,verifier,attestation)
 if not decision.allowed:
  raise PermissionError("Staff gateway authorization incomplete")
 return claims
