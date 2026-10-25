# Phase 16 — Driver, vehicle and delivery-assignment foundation

Introduces driver and vehicle records, restricted order-to-driver assignments, loading-manifest vehicle matching, and a table for future location/status events. Staff-only endpoints can create and inspect assignments. Driver logins, GPS ingestion, routing, customer-visible statuses and electronic proof of delivery are **not yet implemented**.

Dispatch is explicitly disabled while payment verification, stock reservation consumption and custody handoff remain incomplete. GPS fields are schema foundations only; do not claim live tracking is enabled. Before production: scoped driver identity verification, retention/consent policy for precise locations, dispatch and status-transition authorisation, comprehensive integration tests.
