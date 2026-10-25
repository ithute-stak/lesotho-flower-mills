# Phase 42 — Finance operational alerts integration

The opt-in one-shot reconciliation scheduler now evaluates worker run health and unresolved checkout counts on successful completion, then persists deduplicated alerts. The admin reconciliation view reads finance alerts via the existing staff-scoped API.

Env settings: `LFM_ALERT_UNRESOLVED_THRESHOLD` defaults to 5 and `LFM_ALERT_STALE_MINUTES` to 120. The scheduler and worker retain their separate, disabled-by-default feature flags. Neither email/SMS delivery nor an independent alert schedule has been installed. A worker crash marks the run as failed; alert evaluation following that exception is not yet guaranteed. PostgreSQL dedupe integration coverage is included. Alerts do not approve payments or trigger retries.
