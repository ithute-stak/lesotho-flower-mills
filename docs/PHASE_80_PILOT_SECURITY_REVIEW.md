# Phase 80 — Reverse race and controlled pilot security review

Phase 79 CI passed. Added a two-connection PostgreSQL test for cancellation acquiring the order row lock first, followed by checkout attempting the same lock. Cancellation should release stock once and write one immutable audit event; checkout should subsequently read `cancelled` and reject without creating a checkout attempt.

## Current pilot decision: BLOCKED

Validated so far by CI: backend tests, PostgreSQL migrations and integration tests, and builds for customer, admin, warehouse and driver applications. Separate tests check overselling, order conversion, unpaid picking restrictions, order cancellation, audit events and both order-lock race directions. This does **not** verify real-world customer journeys or financial settlement.

External pilot prerequisites still missing: real registered Ithute Auth browser integration with trusted ownership attestation and membership; finance identity end-to-end authorisation; approved tax/pricing; independent IthutePay settlement verification, reversal/refund handling and real payment race testing; full stock custody and dispatch reconciliation; browser journey tests across four apps; backup restoration, incident response and business operational approval.

No production payment or dispatch feature was activated. The reverse race test checks the same order-row-lock contract used by the checkout service, but is not an outbound provider call or a fully routed HTTP integration test.
