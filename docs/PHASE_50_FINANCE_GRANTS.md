# Phase 50 — Database-backed finance grants

Adds a database table for finance_viewer, finance_reviewer and finance_admin grants and request-time checks that deny missing, inactive, and revoked grants. This is deliberately stricter than relying on a JWT role alone: until Ithute Auth is trusted, finance privileges also require an existing administrator token. No default grants are inserted, so protected review endpoints fail closed until an authorised provisioning procedure is established.

Pending: issuer/audience-validated Ithute Auth and live identity membership, grant administration and audit trail, revocation concurrency tests, and appropriate segregation of finance roles across all routes. No payments or delivery releases are enabled.
