# Phase 52 — Finance role administration interface

The admin app now has a **Finance Roles** section. Existing finance administrators can inspect current database grants, request roles for others, and revoke existing grants after confirmation. Grant requests still require a separate reviewer via the API; the UI deliberately does not provide approval until identity and audit controls are strengthened.

The tests cover request-time denial after an inactivated grant is no longer returned by the database. End-to-end grant/revocation database concurrency and a tamper-evident grant change ledger are still outstanding. No initial finance administrator is provisioned automatically. Ithute Auth integration and production role bootstrapping remain blocked.
