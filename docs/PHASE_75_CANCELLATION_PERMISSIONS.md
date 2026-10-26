# Phase 75 — Cancellation permission and multi-product rollback

Phase 74 CI passed. The order cancellation route now requires the existing active finance-administrator grant, checked against PostgreSQL at request time. General staff access alone no longer authorises cancelling orders.

Added integration coverage for a two-product reservation: a deliberately inconsistent inventory balance causes cancellation to fail, and PostgreSQL rollback preserves the order and all earlier reservation balances without creating an audit event. An API test confirms anonymous requests are rejected.

This conservative permission model is temporary: fine-grained cancellation roles, a broader payment-status check, real settlement/refund handling, concurrent cancellation testing and audit review need to be completed before external pilot. Production payments and dispatch are still disabled.
