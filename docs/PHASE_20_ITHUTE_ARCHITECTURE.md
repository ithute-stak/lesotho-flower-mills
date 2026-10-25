# Phase 20 — Verified Ithute service architecture

Inspection date: 2026-10-25.

## Inspected upstream repositories
- [Ithute platform](https://github.com/ithute-stak/ithute): docs/platform-service-clients.md, docs/business-digital-address-oidc.md, packages/ithute-auth-nextjs/README.md.
- [Ithute Pay](https://github.com/ithute-stak/ithute-pay): README.md.

## Verified boundaries
1. Ithute Auth supports managed machine-to-machine clients via POST /v1/auth/service-token, specifying client_id, client_secret, audience and scope. Permissions are explicitly allow-listed. Auth's Next.js App Router SDK is **pre-publication**, and should not be npm-installed as though released. Register a distinct lfm interactive OAuth client with exact callback URI, separate from the machine client.
2. Ithute Pay is the common payment orchestration system. It uses Merchant -> Application -> ApiKey, application-specific test/live credentials and a platform discovery contract at GET /api/v1/platform. Its README identifies https://api.pay.ithute.co.ls as canonical API and application keys ipb_test_ / ipb_live_. Do not embed direct EcoCash, M-Pesa or card credentials in LFM.
3. Do not assume Ithute Documents or notification HTTP APIs exist until their repositories/interfaces and deployment contracts are inspected.

## Integration decision
- LFM retains pricing, inventory, sales, assignment, picking, delivery and discrepancies as system-of-record.
- Ithute Auth owns interactive identity and authentication; LFM keeps authorization based on local verified customer and staff membership. Never auto-link accounts on email.
- Ithute Pay owns provider requests, payment initiation/settlement and provider callbacks. LFM must verify webhook signatures/idempotency and independently reconcile authenticated settlements before a future controlled order confirmation.
- Until credentials, API contracts, signature schemes and integration tests are verified, all integrations remain disabled.

## Migration and controls
1. Register separate Ithute Auth interactive application (approved exact HTTPS callbacks), and if necessary a managed service client with the minimum audience/scopes.
2. Confirm OIDC issuer/JWKS and token audience checks; use server-side Next.js PKCE callback, encrypted HttpOnly session cookies and central immutable sub.
3. Register an LFM-specific Ithute Pay application under the correct merchant (LFM external merchant if applicable), with isolated test keys.
4. Obtain and validate Ithute Pay's actual request/response models, webhook authentication, idempotency and test environment before enabling payment methods.
5. Introduce explicit identity mapping tables and migration with review, never match central identity using email alone.
6. Test failure modes, retries, cancellation/refunds, key rotation and least privilege prior to production.

## LFM-specific constraints
Current local JWT login and sandbox payment endpoints are not production-grade replacements for Ithute services. The integration layer must not bypass existing fail-closed payment, stock and dispatch controls.
