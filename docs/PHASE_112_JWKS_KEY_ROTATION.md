# Phase 112 — JWKS key selection and rotation baseline

Added a fail-closed RS256 JWKS validator that selects exactly one RSA signing key by token key ID (kid), checks signature and registered JWT claims, and rejects unknown/duplicate key IDs or invalid signing keys. Tests cover rotating from an old key to a new key while both keys are published, rejecting tokens after old-key removal, wrong signatures and HS256 confusion.

**Scope boundary:** This stage accepts a separately trusted JWKS document as input. It does not fetch key material over HTTPS, pin an actual Ithute Auth discovery endpoint, cache JWKS, enforce refresh or key expiry, verify live staff membership or MFA, or enable any gateway. Do not feed token-provided jku/x5u URLs to a fetcher. Signing keys must only come from an operator-approved HTTPS issuer via a bounded refresh mechanism with safe outage behaviour.

Phase 111 CI was still pending at first inspection. Administration and warehouse are still blocked at the public edge. External pilot, live payments, refunds and dispatch remain unapproved.
