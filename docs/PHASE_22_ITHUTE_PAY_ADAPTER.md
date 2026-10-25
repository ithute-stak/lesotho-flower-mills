# Phase 22 — IthutePay checkout contract adapter

Inspected in ithute-stak/ithute-pay:
- packages/sdk-python/paybridge/client.py
- apps/backend/routers/payments.py
- apps/backend/routers/checkout.py
- apps/backend/database/schemas/checkout.py
- apps/backend/main.py
- docs/CENTRAL_PAYMENT_PLATFORM.md

Confirmed IthutePay API paths (under /api/v1):
- POST /checkout-sessions and GET /checkout-sessions/{session_id} for hosted checkout.
- POST /payment-intents and GET /payment-intents/{payment_id} for payment intent processing.
- Bearer application API key and Idempotency-Key header.
- Checkout request includes amount, currency, reference, description, expires_in_minutes, optional metadata and redirect URLs.
- Checkout response includes public_id, amount, currency, reference, status and checkout_url.
- IthutePay app API is https://api.pay.ithute.co.ls, but production access/credentials have not been verified.

This phase adds an isolated testable checkout adapter; it is **not exposed as an LFM endpoint**, and does not create real checkout sessions. It rejects mismatched amount/reference/currency responses.

Before activation:
1. Provision LFM-specific merchant/application credentials, separate test/live environments.
2. Build DB-persisted checkout session mapping, idempotency, order total calculation (tax/freight), and safe server-side order lookup.
3. Validate signature requirements, authoritative webhook verification and independent settlement polling.
4. Integrate trusted financial reconciliation and maker/checker release approval.
5. Use automated sandbox tests and forbid return-URL claims as payment evidence.
6. Ensure no secrets, personal data or card details appear in logs or client-side JavaScript.

IthutePay remains the provider-of-record and LFM remains the order/stock system-of-record.
