"""Offline RS256 Ithute Auth token verification with explicitly pinned public key.

This verifier is intentionally not wired into staff admissions yet.
"""
from dataclasses import dataclass
from datetime import datetime,timezone
import jwt
from jwt import InvalidTokenError

@dataclass(frozen=True)
class IthuteAuthTrust:
 issuer:str
 audience:str
 public_key_pem:str

def verify_ithute_token(token:str,trust:IthuteAuthTrust)->dict:
 if not trust.issuer.startswith("https://") or not trust.audience or not trust.public_key_pem:
  raise ValueError("Ithute Auth trust configuration incomplete")
 try:
  untrusted_header=jwt.get_unverified_header(token)
  if untrusted_header.get("alg")!="RS256":
   raise InvalidTokenError("Unsupported token algorithm")
  claims=jwt.decode(token,trust.public_key_pem,algorithms=["RS256"],
    issuer=trust.issuer,audience=trust.audience,
    options={"require":["exp","iat","nbf","iss","aud","sub"]},
    leeway=30)
  now=datetime.now(timezone.utc).timestamp()
  if claims["iat"]>now+30:
   raise InvalidTokenError("Token issued in future")
  if not isinstance(claims["sub"],str) or not claims["sub"].strip():
   raise InvalidTokenError("Missing subject")
  return claims
 except (InvalidTokenError,ValueError,TypeError) as exc:
  raise ValueError("Ithute Auth token verification failed") from exc
