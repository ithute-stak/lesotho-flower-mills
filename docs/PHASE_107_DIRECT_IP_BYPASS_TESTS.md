# Phase 107 — Direct-IP and TCP bypass verification

Phase 106 Full Stack Network Isolation, main CI, Deployment Config and Docker Network Isolation passed.

The full-stack isolation script now probes actual **TCP socket connections**, not only successful HTTP responses. This matters because PostgreSQL and services returning 403/404 can still accept a connection even when an HTTP-only test incorrectly calls them unreachable. For each of admin-web, warehouse-web, API and PostgreSQL, the test attempts both the Compose hostname and the discovered internal Docker IP from an ephemeral peer attached exclusively to the public-edge bridge. A successful TCP connection fails the workflow. An accessible customer service remains a positive control. Cleanup remains automatic.

This test does not establish that the public frontend cannot call internal APIs by design, nor does it test host-level privileges, compromised containers, VPN/MFA, certificate issuance or external perimeter policy. Live financial and dispatch operations and external pilot approval remain blocked.
