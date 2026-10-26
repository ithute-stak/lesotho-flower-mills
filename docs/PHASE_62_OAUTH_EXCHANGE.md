# Phase 62 — OAuth callback preparation and token exchange

Added server-only callback preparation connecting the sealed OAuth transaction to callback state validation, plus a POST authorization-code exchange primitive using the verified upstream `/oauth/token` route and PKCE verifier. Exchange requires pinned HTTPS issuer/callback configuration, no redirects, a short timeout, and validates the basic token response shape. It never logs or persists tokens.

**Not live:** Existing login/callback routes still return 503 and never call these helpers. The replay claim is not yet wired from the Next.js process to PostgreSQL. ID token signature, issuer, audience, nonce, account membership, central-session status, and protected app session issuance remain unimplemented in the web app. The exact upstream token response must be validated in integration tests before this helper is used; in particular whether an ID token is always returned. Do not enable OAuth authentication or payments yet.
