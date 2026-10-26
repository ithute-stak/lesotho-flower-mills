# Phase 71 — Synthetic quote-to-order workflow smoke test

Added `backend/tests/test_order_to_fulfilment_smoke.py`, covering a draft quotation with one bag of a synthetic product, conversion to an unpaid order, one-unit stock reservation, and rejection of warehouse pick-list creation until order confirmation. The test invokes both application modules using a controlled synthetic DB adapter; it does not touch real customer, stock or financial data.

## Evidence register

| Stage | Verification available | Outstanding evidence |
|---|---|---|
| Quotation to order | Synthetic API function smoke test | Full HTTP + PostgreSQL workflow |
| Stock reservation | Synthetic assertion + separate PostgreSQL oversell concurrency test | Ledger accuracy across cancelled orders and dispatch |
| Unpaid-order custody | Synthetic test asserts pick is rejected | Warehouse/driver browser end-to-end tests |
| Tiered price accuracy | Existing module-specific pricing tests | Approved live price books and tax/legal validation |
| Payment settlement | Fail-closed payment architecture | Real sandbox provider settlement and webhook audit |
| Order to delivery | Individual fulfilment/delivery tests | Full integrated authorised lifecycle |
| Central staff authentication | Internal verification helpers | Registered OAuth app, live session, revocation and browser E2E |
| Restore/recovery | Not established | Backup restoration and operational incident drill |

**Pilot decision: Not authorised.** This smoke test deliberately proves only the unpaid-order custody boundary, not the complete commercial lifecycle. Real payment and dispatch remain blocked. Next focus: PostgreSQL fixture-backed quote/order integration, stock release/rollback invariants and a traceable multi-portal E2E test.
