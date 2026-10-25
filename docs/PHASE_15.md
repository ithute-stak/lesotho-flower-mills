# Phase 15 — Provider-neutral payment gateway foundation

- GatewayProvider interface and explicit sandbox implementation.
- Staff-only initiation and provider capability endpoints.
- Sandbox is **off by default** and only enabled with LFM_SANDBOX_PAYMENTS_ENABLED=true.
- Sandbox references are recorded as pending finance transactions; they never represent payment.
- No public card-data collection, live gateway redirect, settlement callbacks, verified transactions, refunds or payment authorisation.
- EcoCash, M-Pesa and card processors require provider contracts, API credentials, certified integration methods, verified signatures and reconciliation before being enabled.
- API must not be relied upon for dispatch or production payments.
