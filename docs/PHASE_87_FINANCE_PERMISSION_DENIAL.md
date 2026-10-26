# Phase 87 — Negative finance permission integration tests

Phase 86 CI, browser smoke and PostgreSQL-backed browser E2E all passed. Added API-level Playwright tests against real FastAPI and disposable PostgreSQL that verify an authenticated local administrator without an active finance grant cannot cancel an order (HTTP 403), and customer or anonymous requests are denied (HTTP 403/401). The order ID is intentionally nonexistent: authorization must reject before the order lookup, ensuring no inventory mutation or payment activity occurs.

The checks deliberately do not create finance grants or activate financial workflows. Positive grant approval, verified Ithute Auth identity, grant revocation and actual order finance flows still require independent end-to-end verification. The external pilot remains blocked.
