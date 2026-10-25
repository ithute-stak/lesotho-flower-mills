# Phase 29 — Final-total audit infrastructure

New append-only finance.total_review_events table with database-level rejection of updates/deletes. Added staff-restricted audit listing and an approval endpoint that enforces distinct maker/checker identities but deliberately fails closed.

There is no claim that independent final total approval is operational. It is blocked until a tax-compliant approved policy, immutable delivery tariff snapshots, role validation through Ithute Auth, transactional approval and PostgreSQL integration tests exist.

IthutePay checkout already requires review_status=approved and the stored gross amount, and thus remains blocked. No automatic payment-to-dispatch transition is available.
