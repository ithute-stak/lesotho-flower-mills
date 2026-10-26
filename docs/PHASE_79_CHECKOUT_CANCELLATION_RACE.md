# Phase 79 — Checkout attempt versus cancellation race

Phase 78 GitHub CI passed. Added a two-connection PostgreSQL test using a shared sales-order row lock. One connection creates a durable checkout attempt while holding that lock; the concurrent cancellation request must reject with HTTP 409 once the checkout is recorded. The test asserts the order remains pending, reserved stock remains unchanged, and no cancellation event is created. The ephemeral test fixture removes the checkout attempt during cleanup.

This exercises the database locking contract shared by checkout initiation and cancellation, not an actual outbound IthutePay request or a full browser OAuth session. A reverse-order checkout-after-cancellation race, genuine payment-provider failures, and external pilot certification remain outstanding. Live payment, refund and physical dispatch features remain disabled.
