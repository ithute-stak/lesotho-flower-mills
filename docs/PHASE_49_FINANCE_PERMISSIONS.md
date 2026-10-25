# Phase 49 — Conservative finance authorisation

Sensitive reconciliation and notification incident APIs now use a dedicated finance access dependency. In the existing local JWT model, **only the admin role** is recognised, rather than the previous blanket admin/sales_manager staff access. Existing sales managers will get 403 for these endpoints. This is a conservative interim policy, not a full dedicated finance reviewer/admin permission hierarchy.

Remaining security work: verify staff accounts and role grants against current database membership, implement centrally verified Ithute Auth, recheck session revocation, introduce separate read/review/approval roles, and use an independently validated maker-checker system. A JWT role assertion alone must not authorise live financial approvals.
