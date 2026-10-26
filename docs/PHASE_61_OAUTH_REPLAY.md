# Phase 61 — Atomic OAuth callback replay prevention

Added a PostgreSQL table with SHA-256 digests of OAuth states and an atomic INSERT ... ON CONFLICT DO NOTHING transaction claim. Concurrent attempts to claim the same state cannot both succeed. Expired states are rejected, and no raw OAuth state is persisted. PostgreSQL integration tests cover simultaneous claims, replay and expiry.

**Not activated:** The current Next.js Ithute Auth login and callback routes still return 503; the claim primitive is not wired to them. Production integration must ensure a shared atomic claim store between the Next.js callback and backend, verify the sealed transaction and state *before* claiming, use a trusted fixed 10-minute expiry, then consume before token exchange. It must enforce nonce validation, central session status, staff membership, and secure server sessions. Scheduled deletion of expired digests is still needed. No live authentication or payment approvals have been enabled.
