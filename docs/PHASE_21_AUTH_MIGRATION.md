# Phase 21 — Ithute Auth migration groundwork

Reference: ithute-stak/ithute/packages/ithute-auth-nextjs/README.md (inspected 2026-10-25).

## Verified service capabilities
- Ithute Auth has server-side Next.js App Router OAuth authorization-code + PKCE wrapper.
- Its SDK is explicitly **not yet published**. Do not add a fake npm dependency.
- Ithute Auth dashboard registers an interactive client with a unique ID, exact HTTPS callback URI and explicit enablement.
- Production session uses encrypted HttpOnly cookies; verify central session state and perform same-origin POST logout.
- Access tokens are not exposed to client-side JavaScript. Product authorization remains LFM responsibility.

## Integration sequencing
1. Create interactive OAuth app 'lesotho-flour-mills-customer' in Ithute Auth and configure exactly the approved customer portal callback, and separate admin/warehouse/driver applications with their own redirect URIs. This requires platform-admin authorisation outside of the LFM repository.
2. Confirm real issuer URL, exact redirect URIs, client registration, session secret and unpublished SDK installation source/version.
3. Integrate server-side PKCE login and callback only after signed JWT issuer, audience, nonce, state and session-revocation tests.
4. Store a reviewed LFM-to-Ithute subject mapping. Never silently link on email.
5. Keep LFM roles and customer/business verification enforced locally.
6. Replace frontend token storage with secure server-side sessions after canary and rollback tests.
7. Decommission legacy login only after all four portals pass E2E tests.

## Current state
No OAuth client registration performed, and no OAuth callback route or central token verifier deployed. Existing login continues in development. This phase adds contract tests and safe configuration readiness checks only.
