# Phase 23 — IthutePay checkout and reconciliation foundation

Added finance.checkout_sessions table to track per-order payment sessions, remote IthutePay session IDs, idempotency, expected amount and status observations. Added staff-restricted checkout initiation and refresh endpoints using the server-side IthutePay adapter.

Security defaults:
- Checkout is off unless LFM_ITHUTE_PAY_CHECKOUT_ENABLED=true and valid test API configuration is supplied.
- Staff only. Customer checkout is not enabled.
- LFM order amount is taken from database, never request payload.
- Provider API key stays server-side; no provider secrets in browser.
- Status refresh validates amount, currency and order reference.
- Even a remote `paid` status is merely an observation: it does **not** mark finance payments verified, authorise stock release or confirm the order.

Outstanding before production:
- Tax/delivery charges, final invoicing and gross order totals (this adapter currently uses subtotal only).
- Real signed webhook verification, settlement reconciliation and refunds/reversals.
- Durable outbox/recovery for crashes after remote session creation but before local DB commit.
- Full PostgreSQL integration/concurrency tests, retry/idempotency replay and tighter status schema.
- Payment URL ownership/domain allowlisting, trusted identity sessions and dedicated finance roles.

Do not enable this feature on real customer transactions until the above controls are complete.
