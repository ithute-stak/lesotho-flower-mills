# Phase 69 — PostgreSQL central identity and finance permission security tests

Added a PostgreSQL integration test covering an active central identity-to-local staff link, successful read-only finance grant verification, then finance grant revocation and staff-link revocation. All created identities are synthetic and removed after the test.

The tests operate at the internal resolver/database layer, **not** a real OAuth login. They do not attest ownership of a real central subject, test a production session-status endpoint or issue browser cookies. A future trustworthy OAuth integration must still ensure signature, issuer, audience, nonce, current central session, attested subject and active local account checks before access. Live payments and finance approvals remain disabled.
