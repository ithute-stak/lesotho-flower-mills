# Phase 46 — SMTP uncertainty and concurrent delivery tests

PostgreSQL integration tests use injected send functions (no SMTP network) to simulate provider disconnects and two simultaneous delivery workers. The expected invariants are that a disconnect marks the delivery **uncertain**, records one attempt, and never retries it automatically; two workers cannot claim the same pending email.

An interrupted process after the `sending` claim but before completion leaves the row in `sending` and needs manual investigation. No automatic reset or retry was introduced. Production SMTP remains disabled until credentials, review procedures and full integration evidence are approved.
