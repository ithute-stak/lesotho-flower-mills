# Phase 60 — Protected OAuth transaction envelope

Added server-only AES-256-GCM sealing/unsealing of short-lived PKCE verification material, nonce and signed state, using a deployment secret of at least 32 bytes. The helper authenticates the ciphertext with an application-specific associated-data value, checks expiry (600 seconds), checks state integrity, rejects malformed ciphertext and exposes Secure, HttpOnly, SameSite=Lax cookie settings.

This is a **storage primitive, not a completed login workflow**. It is not yet connected to OAuth login or callback routes, which remain disabled. An encrypted cookie alone does **not** guarantee single-use transactions: production callback flow must enforce server-side replay prevention and delete the cookie, plus perform nonce and code-verifier validation, central session status, active LFM membership, secure session issuance and live OAuth client registration. Until such checks are implemented and tested, no OAuth request is initiated and no credentials are exchanged.

The existing local login and finance approval restrictions remain unchanged.
