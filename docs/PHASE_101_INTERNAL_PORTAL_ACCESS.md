# Phase 101 — Internal portal network boundary

Phase 100 CI, Browser Smoke, Backend Browser E2E, and Deployment Config passed. The optional Caddy HTTPS edge now rejects connections whose direct peer IP is not in Caddy's built-in private ranges for the administration and warehouse virtual hosts, with HTTP 403. Customer and driver portal policies are unchanged. A regression check guards the presence of these restrictions.

**Important:** Private-range allowlisting is only a preliminary network boundary. It must not be treated as adequate independent authorization. If traffic reaches Caddy through another reverse proxy, load balancer, NAT, or VPN gateway with a private peer address, the network check can admit traffic that originated publicly. Do not trust unvalidated X-Forwarded-For headers. Use a dedicated authenticated VPN or identity-aware gateway, isolate ingress routing, test actual source IP handling, and confirm staff IAM before deployment. Do not expose internal portals to external users based on this configuration alone.

This phase changes repository configuration only; nothing was deployed. No live payment, refund, physical dispatch or external pilot was enabled.
