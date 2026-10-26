"""Staff gateway admission policy: intentionally unavailable until externally attested."""
from dataclasses import dataclass

@dataclass(frozen=True)
class GatewayDecision:
 allowed:bool
 reason:str

def staff_gateway_decision(*,issuer_verified:bool=False,audience_verified:bool=False,
    signature_verified:bool=False,subject_active:bool=False,membership_current:bool=False,
    mfa_verified:bool=False,session_not_revoked:bool=False,
    gateway_deployed:bool=False,security_approved:bool=False)->GatewayDecision:
 checks=(issuer_verified,audience_verified,signature_verified,subject_active,
         membership_current,mfa_verified,session_not_revoked,gateway_deployed,security_approved)
 if not all(checks):
  return GatewayDecision(False,"Independent staff identity gateway verification incomplete")
 return GatewayDecision(True,"All required gateway attestations supplied")

# No route uses this policy to grant access yet: the public proxy stays at HTTP 403.
