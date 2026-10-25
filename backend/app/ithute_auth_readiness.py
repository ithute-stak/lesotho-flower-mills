"""Preflight for central identity integration; does not enable live authentication."""
import os
from urllib.parse import urlsplit

def assess_auth_readiness(env=None):
    env=os.environ if env is None else env
    issuer=env.get("LFM_ITHUTE_AUTH_ISSUER","").strip()
    audience=env.get("LFM_ITHUTE_AUTH_AUDIENCE","").strip()
    jwks=env.get("LFM_ITHUTE_AUTH_JWKS_URL","").strip()
    blockers=[]
    for field,value in (("issuer",issuer),("audience",audience),("jwks",jwks)):
        if not value: blockers.append("missing_"+field)
    for field,value in (("issuer",issuer),("jwks",jwks)):
        if value:
            url=urlsplit(value)
            if url.scheme!="https" or not url.hostname or url.username or url.password or url.fragment:
                blockers.append("invalid_"+field+"_url")
    # The following checks must be established through integration tests and an
    # approved central Auth client registration, never inferred from env vars.
    blockers.extend((
        "central_staff_membership_contract_unverified",
        "central_session_revocation_contract_unverified",
        "oauth_client_registration_unverified",
        "browser_login_callback_logout_e2e_pending",
    ))
    return {"ready":False,"blockers":blockers,"central_auth_enabled":False}
