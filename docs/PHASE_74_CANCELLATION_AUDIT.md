# Phase 74 — Cancellation audit and recovery controls

Phase 73 CI passed. Added sales.order_cancellation_events with a one-event-per-order unique constraint and a PostgreSQL trigger blocking UPDATE and DELETE. A cancellation now writes the staff actor, order and number of released reservations in the same transaction as stock release and status change. Integration testing asserts one audit event after cancellation, and no duplicate on retry.

Existing cancellation route still uses general staff authentication; dedicated cancellation role grants, independent checks for off-platform payments, and multi-product partial-failure rollback tests remain mandatory before external pilot. The audit trigger prevents ordinary UPDATE/DELETE but does not protect against privileged database administrator actions. No paid/confirmed/dispatched order cancellation or refund processing is enabled.
