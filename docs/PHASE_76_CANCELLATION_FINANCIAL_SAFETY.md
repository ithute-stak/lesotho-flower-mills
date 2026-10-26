# Phase 76 — Cancellation financial safety

Phase 75 CI passed. Cancellation now rejects orders with **any** recorded IthutePay checkout session, regardless of session state. This conservative gate avoids releasing inventory where settlement or refunds may exist outside the local order status. The order row remains locked while checkout presence is checked. A PostgreSQL integration test asserts cancellation rejection, unchanged reserved stock, unchanged pending order and absence of cancellation audit events.

The existing order row lock serialises concurrent cancellation requests, and the unique cancellation event constraint also prevents two completed audit records. **A two-client PostgreSQL race test has not yet been added**; concurrent checkout creation and cancellation also need a shared locking protocol. Therefore these changes are not proof of race-free financial settlement. The conservative policy may prevent legitimate cancelled/expired checkout attempts until a reviewed reconciliation workflow is implemented.

No payment, refund, dispatch or central login was activated. External pilot remains blocked.
