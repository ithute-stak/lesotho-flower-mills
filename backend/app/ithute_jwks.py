"""Pinned JWKS verification for centrally issued staff tokens.

The JWKS document is supplied by a separately trusted fetcher; no token-controlled URLs.
"""
from dataclasses import dataclass
import jwt
from jwt import InvalidTokenError
from .ithute_auth_verifier import IthuteAuthTrust,verify_ithute_token

@dataclass(frozen=True)
class JWKSConfig:
 issuer:str
 audience:str

def verify_token_with_jwks(token:str,jwks:dict,config:JWKSConfig)->dict:
 try:
  header=jwt.get_unverified_header(token)
  kid=header.get("kid")
  if header.get("alg")!="RS256" or not isinstance(kid,str) or not kid:
   raise ValueError("Unsupported or missing key identifier")
  if not isinstance(jwks,dict) or not isinstance(jwks.get("keys"),list):
   raise ValueError("Invalid JWKS")
  matching=[key for key in jwks["keys"] if isinstance(key,dict)
            and key.get("kid")==kid and key.get("kty")=="RSA"
            and key.get("use","sig")=="sig" and key.get("alg","RS256")=="RS256"]
  if len(matching)!=1:
   raise ValueError("Unknown or ambiguous signing key")
  public_key=jwt.algorithms.RSAAlgorithm.from_jwk(matching[0])
  claims=jwt.decode(token,public_key,algorithms=["RS256"],
       issuer=config.issuer,audience=config.audience,
       options={"require":["exp","iat","nbf","iss","aud","sub"]},leeway=30)
  if not isinstance(claims.get("sub"),str) or not claims["sub"].strip():
   raise ValueError("Invalid subject")
  return claims
 except (InvalidTokenError,KeyError,TypeError,ValueError) as exc:
  raise ValueError("JWKS token verification failed") from exc
