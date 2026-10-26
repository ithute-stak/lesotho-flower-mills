# Phase 88 — Finance grant revocation and self-grant tests

Phase 87 CI, browser smoke, and backend E2E passed. New PostgreSQL integration tests establish that an unchanged admin identity with an active finance grant can access finance dependencies, then is denied HTTP 403 immediately after that grant is marked revoked; the transaction is rolled back. A separate check verifies that self-grant requests are denied before a request record can be created. Real-backend Playwright tests ensure an admin without a grant cannot list grants, read grant events, or request a new finance role.

The positive and revocation tests exercise permission dependencies with a real PostgreSQL session, not an end-to-end browser revocation process. Independent grant approval and revocation across real authenticated actors and Ithute Auth central identity remain unverified. Production payments and physical dispatch remain disabled; external pilot is blocked.
