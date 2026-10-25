# Phase 41 — Operational alert groundwork

Added a finance.operational_alerts table, configurable threshold evaluator and deduplicated alert persistence helper. Thresholds currently apply to unresolved payment count and failed/stale reconciliation runs; these are operational alerts, not settlement confirmation. Evaluation and persistence helpers are not yet scheduled or integrated into notification delivery. No email, SMS, background job or provider retry is activated. Alert storage does not confer authority to mark transactions paid.
