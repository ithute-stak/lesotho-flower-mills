# Phase 100 — Deployment readiness and security gate review

## Current decision: BLOCKED

Phase 99 main CI passed. Added a dedicated GitHub Actions workflow that validates resolution of base + production Compose and base + production + HTTPS Compose configurations using synthetic environment variables. This is **static validation**, not container start, TLS issuance, endpoint health verification, or a live rollout.

The read-only deployment readiness registry lists eight gates: combined Compose validation, runtime health checks, TLS certificate validation, staff-portal access restrictions, secret rotation, backup restoration, rollback rehearsal, and independent security approval. No gate is self-approved.

## Critical security boundary

The optional Caddy proxy currently supports public DNS endpoints for customer, administration, warehouse and driver portals. Do not deploy the edge to a publicly reachable network until internal portal access restrictions are implemented and verified. TLS alone is insufficient authorization. The production override is mandatory for production preflight. No payment initiation, physical dispatch, or external pilot is approved.

## Follow-up priorities

1. Harden exposure of administration and warehouse portals behind a verified VPN or identity-aware access proxy.
2. Validate TLS/ACME and application health in an isolated deployment.
3. Prove rollback and PostgreSQL backup restoration without compromising audit records.
4. Complete finance, IAM, operations and customer journey approvals.
