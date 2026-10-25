# Phase 44 — Opt-in finance alert email transport

The notification outbox now supports `sending` and `uncertain` states and counts attempts. An explicitly enabled one-shot SMTP sender claims a pending record with `FOR UPDATE SKIP LOCKED`, commits the claim before performing I/O, and sends using authenticated STARTTLS. An uncertain provider outcome is never retried automatically, reducing the chance of duplicate alerts.

Required configuration: LFM_FINANCE_EMAIL_DELIVERY_ENABLED=true, LFM_FINANCE_ALERT_RECIPIENT, LFM_FINANCE_ALERT_SENDER, LFM_FINANCE_SMTP_HOST, LFM_FINANCE_SMTP_USER, LFM_FINANCE_SMTP_PASSWORD, optionally LFM_FINANCE_SMTP_PORT (587). Credentials must be supplied securely at runtime.

No cron job, email delivery schedule or SMTP credentials have been configured. An interrupted worker can leave a record in `sending`; manual review and a safe resolution policy are needed. This is not exactly-once email delivery or a completed retry/dead-letter system. Real charges, financial approval and dispatch remain blocked.
