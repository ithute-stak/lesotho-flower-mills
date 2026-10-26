# Phase 92 — Finance endpoint permissions review

Phase 91 main CI passed. Identified that `payment_authorisation.py` used generic staff authentication for payment ledger writes, payment history reads and payment confirmation. Changed authorization dependencies to finance_review for payment records, finance_read for ledger reads and finance_admin for the disabled order-confirmation action. Added isolated real-backend Playwright denial tests against these three routes for a locally authenticated administrator without active finance grants.

The current order-confirmation handler remains fail-closed regardless of grant. This phase does not enable payment settlement, provider verification, refunds, or dispatch. Further review is needed for checkout initiation, order-total drafts and reconciliation ownership boundaries; an external pilot is not approved.
