"""Separate cryptographic token validation from independently verified staff claims.

Callers may only supply attestation flags from trusted backend services, never
from browser request bodies, cookies, or arbitrary HTTP headers.
"""
from dataclasses import dataclass
from .ithute_token_service import IthuteTokenService
from .staff_gateway_policy import GatewayDecision,staff_gateway_decision

@dataclass(frozen=True)
class StaffAttestation:
 subject_active:bool=False
 membership_current:bool=False
 mfa_verified:bool=False
 session_not_revoked:bool=False
 gateway_deployed:bool=False
 security_approved:bool=False

def verify_staff_access(token:str,verifier:IthuteTokenService,attestation:StaffAttestation)->tuple[dict,GatewayDecision]:
 claims=verifier.verify(token)
 decision=staff_gateway_decision(
  issuer_verified=True,audience_verified=True,signature_verified=True,
  subject_active=attestation.subject_active,
  membership_current=attestation.membership_current,
  mfa_verified=attestation.mfa_verified,
  session_not_revoked=attestation.session_not_revoked,
  gateway_deployed=attestation.gateway_deployed,
  security_approved=attestation.security_approved)
 return claims,decision
