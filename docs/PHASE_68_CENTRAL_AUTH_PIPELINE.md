# Phase 68 — Central authentication pipeline groundwork

Added an internal, fail-closed helper that resolves an LFM staff account only when an upstream caller supplies a verified central identity and positive online session status. Missing, inactive or unlinked identities are rejected; unit tests cover those denials.

**Not production central login:** this helper does not independently verify the token, query Ithute Auth, issue a browser session or activate the login routes. The parameter names are trust assumptions, not cryptographic proofs; never populate them from browser-submitted claims. Secure issuer validation, staff attestation, actual OAuth registration, end-to-end tests and finance approvals remain pending. Local LFM login is unchanged.
