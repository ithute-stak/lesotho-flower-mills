# Lesotho Flour Mills — Release readiness gate (27 October 2026)

**Decision: NOT YET VERIFIED FOR PRODUCTION.** This is an evidence checklist, not a deployment approval.

## Repository evidence

- Customer engagement reporting, repeat-order review, cancellation, audit search, and PDF export code are committed.
- The isolated Backend Browser E2E workflow provisions PostgreSQL, runs Alembic migrations, checks all Alembic heads, runs selected reporting regression tests, waits for the API health endpoint, and runs Playwright tests.
- The browser tests include synthetic management-report interactions and a real API denial test using an ungranted test identity.
- Real loyalty rewards, scheduled purchases and checkout/stock financial effects remain outside the approved scope.

## Required green checks before any deployment decision

1. Confirm every required GitHub Actions **push** workflow for the exact release SHA passed. The connector's combined-status endpoint and pull-request-only workflow-run lookup do **not** prove this.
2. Verify **Backend Browser E2E** passes, including reporting tests, migration-head checks, and finance-denial browser checks.
3. Verify fresh-database Alembic upgrade succeeds, existing-database upgrade is rehearsed using a sanitized copy, and migration rollback hazards are documented. Migrations 0044 and 0045 deliberately refuse audit-destroying downgrade paths.
4. Verify admin frontend builds and report browser downloads run under the deployed API routing setup.
5. Review finance roles and independent-reviewer enforcement; confirm denial behavior for anonymous, customer, and ungranted identities.
6. Confirm planning-only labeling and lack of live reward, purchase, inventory, checkout, and payment side effects.
7. Verify database backup/restore, operational health monitoring, migration runbook, and rollback/deployment procedures.
8. Capture exact SHA, workflow URLs, results, test artifacts, migration result, QA owner, and authorized release approver.

## Evidence gaps at authoring time

No passing status was returned for the latest SHA by the connected combined-status service. The connected workflow-run lookup is restricted to pull-request runs, so an empty response does not mean push workflows passed or failed. No production deployment, migration rehearsal, or payment activation is established by this document.

Release may be signed off **only after** required evidence is attached and reviewed by the responsible project owner.
