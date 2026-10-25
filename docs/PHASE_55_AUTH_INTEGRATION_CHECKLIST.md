# Phase 55 — Central identity verification readiness

Phase 54 CI passed. The existing LFM API still relies on locally signed JWTs, and finance access additionally checks active database grants. Do not describe this as Ithute Auth integration.

Before integrating central authentication, verify Ithute Auth's actual token type, issuer, audience, key rotation and JWKS contract; validate account and staff-membership status on every privileged request; handle session revocation; confirm subject mapping to existing finance grants; and provide tests for expired tokens, wrong issuer and audience, revoked membership and key rotation.

No live payment or final-total approval should be activated until these checks pass. Do not invent Ithute Auth endpoints or credentials.
