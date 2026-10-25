# Phase 31 — PostgreSQL CI integration tests

CI now provisions an isolated PostgreSQL 16 service, upgrades the actual Alembic schema, and runs integration tests against an ephemeral database. The initial checks verify key finance/delivery tables and enforce database financial controls.

The regular unit suite remains separate. This phase is **not** a complete end-to-end payment or warehouse test. No live IthutePay service is used and no credentials are needed.

Next: seed realistic policy/orders through migration-compatible fixtures, test immutable audited approvals and concurrent stock reservations, and validate rollback/upgrade paths.
