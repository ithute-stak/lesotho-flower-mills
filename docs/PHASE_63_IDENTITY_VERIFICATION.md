# Phase 63 — ID token and central session verification

Inspected upstream Ithute Auth `platform/ithute-auth/app/oauth.py` and `platform/ithute-auth/app/account.py`. The OAuth code exchange returns an ID token. Central session checks use `GET /v1/account/session-status`, which reports `{"active":true}` only for active sessions with an enabled application.

Added server-only helpers to verify RS256 ID-token signatures using issuer-pinned HTTPS JWKS, validate issuer/audience/nonce/expiry/issued-at/subject, and perform online central session checks with timeouts and no redirect. No tokens are logged or saved by these helpers.

**Limits:** Authentication routes still return 503. No live LFM client registration, staff membership service, secure app-session issuance, or callback replay wiring is complete. No real OAuth login, central staff authorization or payment activation occurred. Production must independently audit JWT edge cases, verify real public keys, add rotating-key and wrong-key tests, and validate OAuth session revocation and membership end-to-end.
