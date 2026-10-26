# Phase 110 — Staff gateway authentication architecture

Phase 109 main CI, full-stack Docker network isolation, deployment config, Docker isolation and Backend Browser E2E passed (Browser Smoke was still running at first verification).

## Current implementation

Added a pure, default-deny staff gateway policy with nine mandatory inputs: verified issuer, audience and cryptographic signature; active identity and current organisation membership; MFA; unrevoked session; actual gateway deployment; independent security approval. Exhaustive unit tests cover all 512 boolean combinations and ensure the public Caddy virtual hosts for admin and warehouse remain HTTP 403 without proxy routes.

## Architectural boundary

This policy is **not proof of authentication**: boolean input claims must never be accepted directly from a browser, request headers or untrusted services. It is not wired to any web route, and no trusted external Ithute Auth token verification, JWKS retrieval, live membership lookup, gateway deployment, MFA enforcement or production ingress has been implemented. Full server-side verification must be built before any admission is possible.

Admin and warehouse remain unavailable through the public edge. Finance operations, refunds, dispatch and external pilot approval remain blocked.
