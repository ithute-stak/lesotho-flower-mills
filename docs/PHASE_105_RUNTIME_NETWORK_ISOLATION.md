# Phase 105 — Disposable Docker network isolation

Phase 104 main CI, Browser Smoke and Deployment Config passed. Added a GitHub Actions job that creates disposable public and private Docker bridge networks, runs a customer test web server on public and an admin test server on private, verifies customer reachability, and verifies the private admin service cannot be accessed from the public bridge by either DNS hostname or direct private IP. Teardown runs even on failure.

The job separately checks the checked-in Compose source for the dedicated edge network and missing internal portal connections. This **models the network topology** but does not run the full combined Lesotho Flour Mills stack, cannot verify production firewall configuration, host port access, VPN security, trusted identity, and is not evidence of an independently authenticated gateway. Warehouse separation is guarded statically, not probed with a running warehouse service in this phase.

No production deployment, finance activation, public internal-portal access or external pilot approval has occurred.
