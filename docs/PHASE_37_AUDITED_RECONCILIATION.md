# Phase 37 — Reconciliation audit integration

The existing opt-in IthutePay reconciliation worker now writes append-only audit events for observed, mismatched and unreachable session queries. It uses a PostgreSQL transaction-scoped advisory lock to avoid overlapping runs, and commits its batch of observations and local checkout updates atomically. It does not issue charges, verify settlement or confirm orders.

Caveats: the worker is still **not scheduled**, failed session queries are audit observations only, and a single failed transaction causes the batch to roll back. Actual provider credentials, concurrency tests and production operator controls are required before enabling automated execution. No callback authentication or payment authorisation has been enabled.
