# Phase 35 — Payment session reconciliation worker foundation

Added an opt-in server-side function that reads existing IthutePay checkout sessions and validates their order reference, amount and currency. No new charges are created, and provider observations cannot mark an LFM payment verified or confirm an order.

Enable only for isolated testing with `LFM_ITHUTE_PAY_RECONCILIATION_ENABLED=true` and approved test credentials. The function is not scheduled or running in deployment. Entries without provider session IDs (including ambiguous failures before the session ID was recorded) remain unresolved for manual investigation. Production needs an authenticated provider search-by-idempotency contract, safe distributed scheduling/locking, retries with backoff, audit event outbox, signed webhook handling, and independently verified settlement.
