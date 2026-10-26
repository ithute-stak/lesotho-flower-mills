# Phase 73 — Unpaid order cancellation and stock release

Added a staff-protected `POST /api/v1/admin/orders/{order_id}/cancel` route. Under an order row lock, it accepts only `pending_payment` orders, rejects orders with fulfilment pick lists, locks active stock reservations, decreases reserved quantities without modifying on-hand stock, marks reservations `released`, and cancels the order in one database transaction. A second cancellation is rejected, so released stock cannot be released again.

The PostgreSQL integration suite now covers successful release, repeat cancellation denial, unchanged on-hand stock, and rejection of cancellation after an order becomes confirmed.

This route is **not** a refund operation and must not cancel settled, confirmed or dispatched orders. Cancellation authorization currently relies on existing staff authentication; production needs granular cancellation permissions, audit log events, payment/credit hold checks, and multi-reservation failure-injection tests. Live payments, dispatch and external pilot remain blocked.
