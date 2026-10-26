# Phase 91 — Finance role race tests

Phase 90 CI passed. Added real two-connection PostgreSQL tests for concurrent approval of one grant request and concurrent revocation of one active grant. Expected results in each race: one success, one HTTP 409, one corresponding append-only audit event. Approval also asserts exactly one active recipient grant; revocation asserts inactive grant state.

Committed fixture rows are retained only in disposable CI PostgreSQL because finance grant audit history cannot be deleted. The tests refuse database URLs not containing `lfm_test`. These tests do not establish browser-level Ithute Auth attestations or permission revocation across external providers. Financial settlement, refunds, dispatch and external pilot remain disabled.
