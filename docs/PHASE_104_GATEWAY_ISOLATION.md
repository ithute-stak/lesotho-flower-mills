# Phase 104 — Public edge network isolation

Phase 103 main CI and Deployment Config passed. The public HTTPS edge now attaches only to a dedicated `public_edge` Docker network. Customer and driver frontends join that network as well as their application network. Admin and warehouse are not attached to `public_edge`; the public Caddy configuration continues returning HTTP 403 for their virtual hosts with no internal reverse-proxy route.

Static regression checks ensure the edge does not join the default application network. This reduces direct container reachability from the edge, but **is not a runtime bypass test** and does not establish complete container isolation or identity-aware internal access. Host loopback ports, internal Docker peers and operations network paths require an actual isolated deployment test. No production services were deployed or exposed.

Next: run disposable Docker networking tests against resolved Compose configurations, inspect network membership and verify denied requests, then plan an authenticated staff gateway. Live payments, refunds, dispatch and external pilot remain blocked.
