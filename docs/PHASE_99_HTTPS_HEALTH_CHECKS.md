# Phase 99 — HTTPS edge and application health checks

Phase 98 main CI, Backend Browser E2E, and Browser Smoke passed. Added an optional Caddy HTTPS edge with one configured hostname each for customer, admin, warehouse and driver portals. Automatic public TLS requires working DNS, public ACME reachability, approved domains and appropriate firewall restrictions. Added an internal FastAPI health check to the production Compose overlay. Regression tests verify hostnames, port mappings, reverse-proxy destinations and health-check configuration.

The HTTP ports on Caddy are intentionally public for ACME challenges and HTTPS ingress; **do not deploy the edge until security, domain ownership, access controls and external pilot permissions are approved**. The admin and warehouse portal hostnames must additionally be restricted using an approved VPN, IP allowlist or identity-aware proxy; this configuration alone is not sufficient. The existing API and web containers remain loopback-bound through base Compose host ports.

Review resolved configuration without exposing secrets:
```sh
docker compose --env-file .env -f compose.yaml -f compose.production.yaml -f compose.https.yaml config --quiet
```

This phase does not deploy infrastructure, validate real certificates, or approve public access, live payments, refunds, physical dispatch or the external pilot.
