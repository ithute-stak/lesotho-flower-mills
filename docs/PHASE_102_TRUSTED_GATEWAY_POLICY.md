# Phase 102 — Trusted access gateway policy and fail-closed edge

Phase 101 main CI and Deployment Config passed. The earlier Caddy restriction used private-range peer IP checks, which can be unsafe behind proxy/NAT because private upstream addresses do not establish user identity.

## Hardened behaviour

The optional public Caddy edge now **always returns HTTP 403** on administration and warehouse virtual hosts. Their `reverse_proxy` upstream directives were removed entirely. This ensures public requests cannot reach those applications through the optional edge even when the incoming peer is private. Customer and driver routing remains unchanged.

## Required gateway design (not implemented)

Before enabling internal portal access: deploy a dedicated authenticated identity-aware gateway or VPN with isolated ingress, verify trusted issuer/audience and staff membership at request time, enforce MFA, verify session termination/revocation, reject spoofable identity forwarding headers, test bypasses from direct container access and all proxy hops, and obtain independent security approval. Internal portals should not be restored to public edge routing.

These repository changes do not deploy a gateway, enable access, obtain TLS certificates, or approve any external pilot. Financial and physical dispatch operations remain blocked.
