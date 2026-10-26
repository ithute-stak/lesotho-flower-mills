# Phase 114 — JWKS DNS preflight and transport safety

Phase 113's six most recent workflows passed. This phase adds a DNS resolution validator rejecting missing, private, loopback, link-local and mixed private/public resolved IP addresses. Tests exercise public, private, metadata and mixed DNS responses.

**Security-critical limitation:** A DNS preflight alone cannot prevent DNS rebinding between resolution and the HTTPS handshake. Consequently the default JWKS fetch now **fails closed**, refusing network access when no explicitly supplied client exists. Injected mock HTTP clients remain usable in isolated tests. Production trust establishment requires an audited transport that pins approved destination IPs at actual socket connection time, maintains original-host TLS SNI and certificate verification, prevents redirects and proxy bypass, and rechecks on rotation. The actual Ithute Auth hostname, issuer metadata and JWKS endpoint have not been verified.

No live integration or public staff gateway admission is enabled. External pilot, finance and dispatch remain blocked.
