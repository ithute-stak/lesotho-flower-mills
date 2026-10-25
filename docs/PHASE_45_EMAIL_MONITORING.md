# Phase 45 — Email notification delivery investigations

The finance reconciliation administration screen now displays the most recent email delivery attempts, states, retry counts, alert codes and safe diagnostic summaries. The API remains staff-restricted and read-only. A PostgreSQL integration test checks uniqueness of alert references and allowed state constraints; it does not yet simulate SMTP transport or simultaneous claim transactions.

Production delivery remains disabled by default. No automatic retry is permitted for `sending` or `uncertain` messages, which can indicate a crash or a provider acknowledgement lost in transit. Review procedures, provider-independent delivery confirmation, and stronger finance-specific access controls are still required.
