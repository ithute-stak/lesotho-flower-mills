# Phase 51 — Finance role governance

Added a database-backed maker/checker flow: existing finance administrators may submit grants for **other** subjects, another administrator approves them, and current grants can be revoked. Every protected finance request re-reads active grants from PostgreSQL so revocation takes effect on subsequent requests.

**Important limitation:** No finance administrator is provisioned by default, meaning the grant API is inaccessible until an independently audited, operator-approved bootstrap mechanism is designed. Grant requests currently store request and approval details but do not have a fully immutable event ledger. Identity subjects are not yet validated against central Ithute Auth. Do not manually bypass safeguards in production. Grant application requires validated staff membership, stronger audit evidence and integration tests before enabling payments.
