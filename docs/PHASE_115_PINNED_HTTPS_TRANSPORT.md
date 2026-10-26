# Phase 115 — Pinned HTTPS JWKS transport prototype

Phase 114 CI was in progress when reviewed. Added a standalone connection-pinned transport which validates all resolved DNS addresses, selects a global IP, connects directly to that address, and performs TLS SNI and standard certificate verification against the original approved hostname. Disallows redirects, non-JSON responses, oversized payloads and untrusted URL forms. Unit tests use injected connections rather than external network.

**Important limitation:** This transport is not wired to the JWKS cache or staff gateway. It must not be considered production-ready until operator-approved issuer metadata, DNS controls, HTTP response semantics, key-validation integration, CA trust and a real test environment have been reviewed. There is no live Ithute Auth request or production activation. Admin and warehouse remain blocked; live payments, refunds, dispatch and external pilot are unapproved.
