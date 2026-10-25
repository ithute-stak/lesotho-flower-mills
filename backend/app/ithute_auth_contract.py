"""LFM server-side Ithute Auth integration preflight.

This module intentionally cannot mint local tokens, change users, or use
unpublished Ithute SDKs. It validates prerequisites for a future OIDC adapter.
"""
import os
from dataclasses import dataclass
from urllib.parse import urlsplit


def https_url(value: str) -> bool:
    url = urlsplit(value)
    return (url.scheme == "https" and bool(url.hostname)
            and url.username is None and url.password is None
            and not url.fragment and not url.query)


@dataclass(frozen=True)
class OIDCReadiness:
    ready_for_registration: bool
    missing: tuple[str, ...]


def preflight(config: dict[str,str] | None = None) -> OIDCReadiness:
    values = config if config is not None else os.environ
    required = ("LFM_ITHUTE_AUTH_ISSUER","LFM_ITHUTE_AUTH_CLIENT_ID",
                "LFM_ITHUTE_AUTH_CALLBACK_URL","LFM_ITHUTE_AUTH_SESSION_SECRET")
    missing = [key for key in required if not values.get(key)]
    if values.get("LFM_ITHUTE_AUTH_ISSUER") and not https_url(values["LFM_ITHUTE_AUTH_ISSUER"]):
        missing.append("valid_https_issuer")
    if values.get("LFM_ITHUTE_AUTH_CALLBACK_URL") and not https_url(values["LFM_ITHUTE_AUTH_CALLBACK_URL"]):
        missing.append("valid_https_callback")
    if values.get("LFM_ITHUTE_AUTH_SESSION_SECRET") and len(values["LFM_ITHUTE_AUTH_SESSION_SECRET"].encode()) < 32:
        missing.append("session_secret_at_least_32_bytes")
    # Readiness means configuration prerequisites only, not a working login.
    return OIDCReadiness(ready_for_registration=not missing,missing=tuple(missing))
