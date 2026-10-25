"""Strict opt-in external JWT verifier. Not wired to current login."""
import os
import jwt
from fastapi import HTTPException

def verify_external_identity(token, key_client=None):
    issuer=os.getenv("LFM_ITHUTE_AUTH_ISSUER")
    audience=os.getenv("LFM_ITHUTE_AUTH_AUDIENCE")
    jwks_url=os.getenv("LFM_ITHUTE_AUTH_JWKS_URL","")
    if not issuer or not audience or not jwks_url.startswith("https://"):
        raise HTTPException(503,"External identity is not configured")
    try:
        header=jwt.get_unverified_header(token)
        if header.get("alg")!="RS256" or not header.get("kid"):
            raise ValueError("Invalid algorithm or key identifier")
        client=key_client or jwt.PyJWKClient(jwks_url,timeout=5)
        key=client.get_signing_key_from_jwt(token).key
        identity=jwt.decode(token,key,algorithms=["RS256"],issuer=issuer,
                            audience=audience,options={"require":["sub","exp","iat","iss","aud"]})
        if not isinstance(identity.get("sub"),str) or not identity["sub"].strip():
            raise ValueError("Invalid subject")
        return identity
    except Exception as exc:
        raise HTTPException(401,"External identity verification failed") from exc
