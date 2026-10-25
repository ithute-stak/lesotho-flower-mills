# Phase 48 — Notification incident management UI

Added review controls to the existing staff Reconciliation screen. For interrupted, uncertain or failed email outbox records, staff can view append-only incident history and submit a classification with a required note. The original message state is never changed, no SMTP request is triggered, and an incident note cannot authorise payment.

This remains protected by the existing staff authentication mechanism, not yet a dedicated finance-only role. Delivery evidence verification and production SMTP remain outstanding.
