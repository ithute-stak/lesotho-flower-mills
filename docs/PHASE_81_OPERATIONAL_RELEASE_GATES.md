# Phase 81 — Operational readiness evidence register

Phase 80 CI passed. Added `backend/app/release_gate_register.py` defining the minimum evidence, owner and target for each demo/pilot gate. Every gate starts `unverified`; this read-only register does not accept self-submitted approvals and cannot enable payments, dispatch or release status.

## Executable browser E2E plan

1. Customer web: synthetic registration, quantity price display and order placement, with no live payment.
2. Admin web: staff sign-in, approved price publication, quotation review, read-only finance dashboard and cancellation permission rejection.
3. Warehouse web: stock receipt, reservation counts, pick-list restriction for unpaid orders, loading quantities, and stock ledger comparison.
4. Driver web: authorised delivery assignment, proof of delivery, dispute handling and mobile layout checks using fake consignments.
5. Cross-app: verify every transition in PostgreSQL; exercise retries, expired sessions, duplicate requests, stock shortage, cancellation and failure recovery.

## Evidence acceptance

Each gate needs reproducible CI results or independently signed QA records, environment/build reference, tester and date, expected vs actual outcomes, and documented remediation for failures. CI success alone does not indicate pilot readiness. No browser E2E runner or independent approval workflow was installed by this phase.

## Decision

Internal demo: unverified. External pilot: blocked. Production: blocked. Next implement automated browser tests against an isolated test environment and gate evidence review without altering existing financial restrictions.
