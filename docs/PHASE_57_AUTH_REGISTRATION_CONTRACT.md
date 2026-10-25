# Phase 57 — Actual Ithute Auth OIDC contract verification

Inspected upstream `platform/ithute-auth/app/main.py` and `platform/ithute-auth/app/oauth.py`. The source defines:

- `GET /.well-known/openid-configuration`
- `GET /.well-known/jwks.json`
- `GET/POST /oauth/authorize`
- `POST /oauth/token`
- OAuth authorization-code with PKCE S256 and RS256 signed ID tokens.

Added an offline discovery-document validator that requires a pinned HTTPS issuer and expected endpoint origin, paths and RS256. Unit tests cover a valid contract and malicious/mismatched metadata.

**Not yet complete:** No live Ithute Auth application was registered or enabled; no credentials, callback hostname or active production issuer were supplied. The upstream Next.js SDK remains unpublished. Live endpoint behavior, actual registration, employee membership checks, central revocation and end-to-end browser login remain unverified. Do not wire central tokens into privileged LFM routes based only on this offline validation. Current local login and financial fail-closed protections stay in place.
