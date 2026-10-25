"""Validate OIDC discovery metadata for dedicated Lesotho Flour Mills registration.

This is an offline preflight helper, never an application-registration request.
"""
from urllib.parse import urlparse

def validate_oidc_discovery(document:dict,issuer:str)->list[str]:
    errors=[]
    if not issuer.startswith("https://") or document.get("issuer")!=issuer.rstrip("/"):
        errors.append("issuer_mismatch")
    expected={
        "authorization_endpoint":"/oauth/authorize",
        "token_endpoint":"/oauth/token",
        "jwks_uri":"/.well-known/jwks.json",
    }
    for field,suffix in expected.items():
        value=document.get(field)
        if not isinstance(value,str):
            errors.append("missing_"+field)
            continue
        parsed=urlparse(value)
        base=urlparse(issuer)
        if parsed.scheme!="https" or parsed.netloc!=base.netloc or parsed.path!=suffix or parsed.query or parsed.fragment:
            errors.append("invalid_"+field)
    if "RS256" not in document.get("id_token_signing_alg_values_supported",[]):
        errors.append("rs256_support_not_confirmed")
    return errors
