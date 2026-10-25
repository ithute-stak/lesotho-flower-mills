# Phase 34 — Durable checkout initiation

Checkout initiation now records a unique per-order attempt and commits it **before** calling IthutePay. Concurrent requests and retries for the same order fail closed rather than initiating another provider payment. Attempts are either initiating, created or reconciliation_required. A staff-scoped status endpoint exposes the attempt state without credentials.

This explicitly handles ambiguous remote outcomes: if the provider call fails, the attempt remains and must be reconciled, never automatically retried. A crash between remote creation and local checkout-session commit can still require human investigation using the persisted idempotency key; there is not yet an automated recovery worker or provider search-by-idempotency contract. Operational/manual recovery procedures, controlled refunds, settlement verification and E2E failure-injection tests are still needed. Live payments and dispatch remain disabled by default.
