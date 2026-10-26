# Phase 111 — Ithute Auth cryptographic token verification

Phase 110 main CI and Full Stack Network Isolation passed. Added a standalone offline token verifier accepting only RS256 and a configured trusted PEM public key, HTTPS issuer and exact audience. It validates signature, issuer, audience, expiry, not-before, issued-at and subject. Regression tests create ephemeral RSA keys and cover a valid token, wrong issuer/audience, expiry, empty subject, future issue date, incorrect signing key and HS256 algorithm confusion. Added the PyJWT RSA cryptography dependency.

**Not an operational identity integration.** The sample issuer `https://auth.ithute.example` exists only in tests. The verifier does not retrieve trusted Ithute Auth JWKS, rotate keys, call membership/session revocation APIs, prove MFA, resolve central staff links or connect to the admission gateway. Its inputs must come from operator-controlled configuration and verified provider metadata, never untrusted request headers. The public Caddy proxy continues to deny admin and warehouse requests.

Production deployment, live finance, refunds, physical dispatch and external pilot remain unapproved.
