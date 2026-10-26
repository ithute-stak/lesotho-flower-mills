# Phase 77 — Financial activity barriers for order cancellation

Phase 76 CI passed. The cancellation service now rejects orders with any existing checkout attempt, checkout session, payment transaction, or payment/credit authorisation, even when the order itself remains in pending_payment. This strengthens the fail-closed boundary: payment or credit activity requires independent financial reconciliation before stock is released.

Both IthutePay checkout initiation and sandbox gateway initiation already acquire an exclusive PostgreSQL row lock on the sales order before creating financial records, as does cancellation. This provides a common order-lock serialization point for these paths. Integration tests cover attempts and payment transactions; checkout-session coverage was introduced in Phase 76.

**Unverified:** There is no multi-connection concurrent cancellation-versus-checkout regression test yet. Other write paths, provider callbacks, and transaction boundaries must be audited for lock-order consistency. This phase does not enable live settlement, refunds or dispatch. External pilot remains blocked.
