# Phase 38 — Reconciliation scheduling and operational controls

A one-shot reconciliation command was added: from `backend/`, run `python -m app.reconciliation_scheduler`. It is **disabled by default** and exits without connecting to database or payment service unless both LFM_RECONCILIATION_SCHEDULER_ENABLED=true and LFM_ITHUTE_PAY_RECONCILIATION_ENABLED=true.

No cron job, systemd timer or Docker scheduled task was installed. A future external scheduler may run it no more than hourly after operational approval. The underlying worker holds a PostgreSQL transaction-scoped advisory lock, which a new integration test checks across two database connections. Console output includes only a basic outcome summary and does not expose credentials.

Still missing: verified production IthutePay credentials, distributed per-attempt backoff/retry policy, alert delivery, metrics dashboards, worker status persistence, signed webhooks, authenticated settlement proof and operator procedures. This command cannot create payments or confirm orders.
