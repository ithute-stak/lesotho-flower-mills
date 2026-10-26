# Phase 72 — PostgreSQL order and inventory integrity

Added `backend/tests/integration/test_order_inventory_integrity.py`, a real PostgreSQL fixture-backed test of order creation using synthetic customer, product, price book, warehouse, quotation and stock balances. Fixtures run inside an outer transaction and are rolled back; no production inventory or payment data is used.

The tests verify: converting a draft quotation results in an unpaid order and a single correct reservation; converting it again is rejected without additional reservations; insufficient stock results in HTTP 409, no sales order and no reserved stock. The repository already separately tests concurrent stock reservations against overselling.

**Limits:** These tests do not complete a payment, approve credit, generate a real pick list, release stock, dispatch a vehicle or confirm delivery. They are backend integration checks, not a business pilot authorisation. Additional failure-injection tests for partial multi-line reservations, order cancellation/release and cross-portal end-to-end testing remain outstanding. The live settlement and identity gates must remain closed.
