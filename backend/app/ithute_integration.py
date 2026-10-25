"""Feature-gated, explicitly configured Ithute service integrations.

This module does not contact remote services or grant authorisation. It provides
a single place for integration readiness validation before any future adapter
is connected to critical LFM order, payment or delivery workflows.
"""
import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class IthuteIntegration:
    auth_enabled: bool
    auth_issuer: str | None
    pay_enabled: bool
    pay_api_url: str | None

    @staticmethod
    def configured() -> "IthuteIntegration":
        auth_enabled = os.getenv("LFM_ITHUTE_AUTH_ENABLED") == "true"
        pay_enabled = os.getenv("LFM_ITHUTE_PAY_ENABLED") == "true"
        auth_issuer = os.getenv("LFM_ITHUTE_AUTH_ISSUER")
        pay_url = os.getenv("LFM_ITHUTE_PAY_API_URL")
        if auth_enabled or pay_enabled:
            # Deliberate fail closed: configuration is not evidence of a secure
            # completed OIDC/payment integration.
            raise RuntimeError("Ithute integrations require verified adapters and integration tests before enablement")
        return IthuteIntegration(auth_enabled, auth_issuer, pay_enabled, pay_url)


def is_https_endpoint(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
