# Phase 113 — Bounded trusted JWKS retrieval and caching

Phase 112's six workflows (CI, Browser Smoke, Backend Browser E2E, Docker Network Isolation, Full Stack Network Isolation and Deployment Config) passed. This phase adds a standalone operator-pinned HTTPS JWKS retriever with a cache TTL restricted to 1–900 seconds, no redirects, no proxy environment inheritance in its default client, bounded response size and key count, and fail-closed refresh handling. Mock HTTP tests cover cached reuse, key rotation, expiry, outage, redirects, unsafe URLs and duplicate key IDs.

This retriever is **not connected to the live Ithute Auth provider or the staff gateway**. Production use additionally requires an approved fixed hostname and JWKS path, DNS/IP resolution controls against server-side request forgery and rebinding, CA verification, verified discovery metadata, key rollover and revocation policy, and service ownership review. The current URL guard rejects literal private IP addresses but does not pin DNS resolutions, so the implementation must not be treated as production-ready for arbitrary supplied URLs. Callers must never derive the JWKS URL from JWT claims or token headers.

Admin and warehouse remain blocked through public Caddy. Production deployment, payments, refunds, dispatch and external pilot remain unapproved.
