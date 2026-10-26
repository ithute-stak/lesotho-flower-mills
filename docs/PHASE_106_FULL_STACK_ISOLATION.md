# Phase 106 — Full-stack Docker network isolation CI

Phase 105 main CI, Backend Browser E2E, Browser Smoke, Deployment Config, and Docker Network Isolation all passed.

This phase adds a full-stack CI workflow that builds and starts the actual PostgreSQL, FastAPI, customer, admin, warehouse and driver containers using base, production, and HTTPS Compose overlays (without publicly starting Caddy). It verifies actual Docker network membership, confirms customer connectivity from a disposable public-edge peer, and attempts direct access by service hostname to admin, warehouse, API and database. The workflow always tears down containers and volumes.

**Limitations:** This is an isolated GitHub Actions test, not a live deployment. It does not prove public network/firewall isolation, reverse-proxy certificate handling, privileged-host bypass resistance or staff gateway authentication. The container access probe primarily tests service DNS and HTTP reachability; production VPN/MFA and direct-IP penetration testing still require independent verification. Payment and dispatch approval remain blocked.
