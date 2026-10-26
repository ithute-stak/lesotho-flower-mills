# Phase 90 — Complete finance permission lifecycle

Added rollback-only PostgreSQL integration coverage for the finance role lifecycle. Separate synthetic maker, checker and recipient identities are used. Verify recipient initially denied; maker submits a finance_viewer request; maker cannot approve; independent checker approves; recipient gets finance_read but never finance_admin; recipient cannot self-revoke; checker revokes; recipient immediately loses finance_read without token change; repeat revocation is rejected; and requested, approved, and revoked audit events identify actors.

Production roles are not provisioned, no external Ithute Auth or financial transactions are exercised. This integration test calls route handlers directly using synthetic identities and a disposable PostgreSQL transaction; external pilot remains blocked.
