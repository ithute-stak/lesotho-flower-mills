# Phase 10 — Stock reservation foundation

Implemented:
- Warehouses, stock balances, stock reservations and sales order records.
- Database CHECK constraint: 0 <= reserved <= on_hand.
- Conditional atomic stock reservation UPDATE with availability check.
- Staff-only quotation-to-order conversion, with row locking, multiple lines and full transaction rollback on unavailable stock.
- New orders are PENDING_PAYMENT and **not paid, dispatched or confirmed**.
- Unit tests for reservation and access controls.

Important limitations:
- There is no authorised stock receiving or adjustment posting yet; stock balance creation is an operations prerequisite.
- No stock movement ledger, multi-warehouse allocation, reservation expiry, cancellation/release flow, payment integration or credit approval.
- Draft quotations do not yet include delivery fees, taxes or official issuance; converting drafts must not be enabled for live customer orders until commercial controls are finished.
- The initial stock table tracks integer bags/units and is not suitable for weighed fractions without an additional unit model.
- Concurrent reservation logic depends on PostgreSQL atomic UPDATE plus unique keys/check constraints and requires real PostgreSQL integration tests before production.
