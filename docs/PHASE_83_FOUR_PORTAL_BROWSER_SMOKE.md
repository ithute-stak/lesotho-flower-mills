# Phase 83 — Four-portal browser smoke coverage

Phase 82 CI and Browser Smoke both passed. Extended the Playwright test server configuration to run customer, admin, warehouse, and driver Next.js applications on isolated ports 3100–3103. Added unauthenticated browser checks for warehouse and driver sign-in boundaries, and configured browser CI to install dependencies for both apps.

These are basic, browser-rendered unauthenticated checks only. They do not test stock receipt, actual picking, delivery, authenticated staff roles or proof of delivery. A fully provisioned sandbox backend and synthetic user identities are still needed for genuine end-to-end testing. No payments or dispatch were activated.
