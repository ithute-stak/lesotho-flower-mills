# Phase 93 — Checkout and order-total permission hardening

Phase 92 CI, Browser Smoke, and Backend Browser E2E passed. Replaced generic staff identity dependencies on staff-facing checkout initiation, checkout attempt reads, checkout status refresh, order-total draft write and reads, order-total preview, sandbox payment initiation and provider listing. Finance Reviewer (or Administrator) is required for mutation/reconciliation operations, and Finance Viewer (or higher) for financial reads. Added isolated real-backend tests that expect HTTP 403 for an administrator without active grants against the checkout, gateway and total-review routes.

All financial operations remain fail-closed subject to their pre-existing commercial and deployment checks. This is not settlement evidence, does not enable checkout, payments, refunds or dispatch, and is not approval for any external pilot. The permissions matrix must still be independently reviewed with the operational finance team.
