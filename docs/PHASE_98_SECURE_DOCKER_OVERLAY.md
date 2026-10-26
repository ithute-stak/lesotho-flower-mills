# Phase 98 — Controlled Docker deployment overlay

Phase 97 introduced fail-closed production preflight. This phase adds `compose.production.yaml` as an explicit deployment override that activates `LFM_ENV=production`, disables sandbox and IthutePay initiation flags, disallows E2E seeding, and drops Linux capabilities while preventing privilege escalation for API and portal containers. Host ports in the base Compose remain bound to 127.0.0.1.

## Mandatory invocation

```bash
docker compose --env-file .env -f compose.yaml -f compose.production.yaml config --quiet
docker compose --env-file .env -f compose.yaml -f compose.production.yaml up -d --build
```

The baseline `compose.yaml` alone **does not enable production preflight**; never deploy using only the baseline. Supply strong unique credentials by protected environment injection, not committed files. Arrange TLS at a separate reverse proxy before exposing any web frontend. These changes **do not configure HTTPS**, a secrets manager, container non-root users, automated backup, image signing, or a production release mechanism. Independent review is required before real deployment.

No payment, refunds, dispatch or external pilot was enabled.
