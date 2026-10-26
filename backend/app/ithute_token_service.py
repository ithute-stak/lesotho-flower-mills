"""Trusted JWT verification using the pinned, bounded JWKS cache.

This is a standalone integration point, not an HTTP admission endpoint.
"""
from dataclasses import dataclass
from .ithute_jwks import JWKSConfig,verify_token_with_jwks
from .ithute_jwks_cache import TrustedJWKSCache

@dataclass
class IthuteTokenService:
 issuer:str
 audience:str
 cache:TrustedJWKSCache

 def verify(self,token:str)->dict:
  if not self.issuer.startswith("https://") or not self.audience:
   raise ValueError("Issuer and audience must be configured")
  try:
   return verify_token_with_jwks(token,self.cache.get(),JWKSConfig(self.issuer,self.audience))
  except (ValueError,TypeError) as exc:
   raise ValueError("Trusted staff token verification failed") from exc
