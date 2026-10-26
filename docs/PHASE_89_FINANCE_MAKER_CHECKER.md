# Phase 89 — Finance permission maker/checker integration

Phase 88 CI, Browser Smoke and Backend Browser E2E passed. Added disposable PostgreSQL integration test that creates separate synthetic maker, checker and recipient identities. The maker requests the finance_viewer grant for the recipient; the maker and recipient cannot approve it (HTTP 403). A distinct reviewer approves, creating an active grant and immutable grant audit events, and repeat approval returns HTTP 409. All database changes are enclosed in an outer transaction rolled back at test completion.

The test directly invokes finance dependency and route functions with synthetic identities. It does not prove the entire browser-based workflow or externally attested Ithute Auth identities. The test does not bootstrap production finance roles. External pilot remains blocked; live payment, refunds and dispatch remain disabled.
