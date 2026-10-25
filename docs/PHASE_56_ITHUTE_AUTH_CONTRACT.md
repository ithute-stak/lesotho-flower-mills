# Phase 56 — Ithute Auth contract verification

Inspected the upstream Ithute repository's `packages/ithute-auth-nextjs/README.md`, `docs/business-digital-address-oidc.md` and `docs/identity-invitations.md`.

Verified from upstream documentation: the Next.js App Router SDK is planned around OAuth authorization-code + PKCE, server-only configuration, exact registered callbacks, encrypted HTTP-only session cookies, and an online central-session status check on `getSession()`. The package is **not published**; its implementation and deployment must be independently validated before integration. Central account provisioning invitations are a distinct service-client flow, not proof of active LFM staff membership.

Added `app.ithute_auth_readiness.assess_auth_readiness` and unit tests: even plausible issuer/audience/JWKS configuration cannot assert production readiness while central membership, session revocation, OAuth client registration and browser E2E tests remain unresolved.

No Auth issuer, JWKS path, callback domain, API credentials or staff roles were invented. The live LFM app still uses local login and current finance grant checks. The unpublished SDK is not installed, and real checkout/final-total approval remains blocked.

## Integration acceptance criteria

- Confirm actual issuer, supported algorithms, JWT/JWKS location, audience, token lifetimes and key rotation in running Ithute Auth.
- Register and enable a dedicated LFM application with an exact HTTPS callback.
- Confirm active LFM employee membership and role revocation using a documented protected central API or verified session contract, on every privileged request.
- Keep OAuth tokens inside the Next.js server session; do not move them into browser localStorage.
- Test login/callback/logout, revoked session, disabled app, wrong audience, expired token, Auth outage and central role removal.
- Only then replace local authorisation deliberately, with rollback and migration planning.
