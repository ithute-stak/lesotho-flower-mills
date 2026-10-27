# Restricted staging deployment gate

All seven workflows on main revision 6a6e9f7 passed on 27 October 2026. This is test evidence only, not deployment approval.

## Before staging

1. Use a disposable, isolated host and a **staging-only** database. Obtain approval from the environment owner.
2. Supply all Compose-required environment values securely. Use staging subdomains with working DNS, verified firewall and Caddy TLS. Do not copy live production customer or payment credentials into staging.
3. Leave `LFM_SANDBOX_PAYMENTS_ENABLED=false`, `LFM_ITHUTE_PAY_CHECKOUT_ENABLED=false`, and `LFM_E2E_SEED=false`. Production Compose enforces all three; the preflight explicitly rejects inconsistent staging flags.
4. From the repository root, with the values exported, run `bash deploy/staging_preflight.sh`. It checks required variables and Compose syntax; it does not deploy.
5. Verify backup restore, controlled migrations, application health, scoped access, browser flows, DNS/TLS and rollback in the isolated environment before inviting testers.
6. Capture evidence and independent sign-off for each release gate. A green CI does not authorise external pilot, payment, refund, dispatch or production use.

## Explicit limitations

The existing `compose.production.yaml` sets `LFM_ENV=production` inside the API container, even when it is used as an overlay on an isolated staging host. That is acceptable for testing production-like *restrictions* only; it does not constitute a dedicated staging environment. The preflight checks the host environment and cannot independently audit credentials, DNS ownership, firewall rules, or the live infrastructure. No host was provisioned or deployed in this change.
