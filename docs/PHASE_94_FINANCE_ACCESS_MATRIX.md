# Phase 94 — Finance access matrix regression

A code-level registry enumerates 22 sensitive finance endpoints and their required dependencies: finance_read, finance_review or finance_admin. A unit test checks that each handler actually declares the specified FastAPI dependency, so accidental replacement with generic staff authorization fails CI. The hierarchy of grant dependencies is also guarded. This supplements the negative real-backend tests introduced in Phases 87–93, but is not an exhaustive independent authorization penetration test.

The matrix covers payment ledger operations, checkout, order totals, payment gateway, finance grant requests, unpaid order cancellation and finance reconciliation review. Operational authorization of other modules, positive role-by-role browser tests, signed Ithute Auth membership and finance business approval remain open. No live financial activity, dispatch or external pilot was enabled.
