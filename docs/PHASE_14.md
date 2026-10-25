# Phase 14 — Payment ledger (secure first slice)

Added:
- Finance schema: uniquely referenced payment records and order authorisations.
- Staff-entered payments remain PENDING, never automatically verified.
- Order confirmation checks verified payment totals, but intentionally fails closed until tax, delivery and trusted provider verification are implemented.
- Payments can be inspected by authorised staff.

Missing:
- Actual signed/verifiable M-Pesa, EcoCash, card or bank webhook integrations.
- Reconciliation, refunds, disputes, final tax and delivery calculation.
- Approved credit account limits and multi-person credit authorisation.
- Robust finance role segregation and audit metadata.
- Full PostgreSQL integration tests.

No order can be legitimately marked paid via the newly added API. Do not deploy this as a payment processing system.
