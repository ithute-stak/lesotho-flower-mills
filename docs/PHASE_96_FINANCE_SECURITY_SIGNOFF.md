# Phase 96 — Finance security assessment and independent sign-off

**Decision: NOT APPROVED.** Passing automated tests does not authorize financial operations or a customer-facing pilot.

## Evidence established
Phase 95 main CI, Browser Smoke and Backend Browser E2E all passed. Earlier integration coverage includes finance permission roles, role revocation, independent maker/checker checks, double approvals and revocations, unauthorised API denials, and checkout/cancellation order locking. These results validate selected code and test environment behaviours, not production controls.

## Release-blocking gaps
1. Verify Ithute Auth issuer/audience, session lifecycle, identity ownership, staff membership removal and signed trust across all apps.
2. Independently approve tax, delivery-fee, discount and final payable calculation policy.
3. Prove authentic settlement, payment webhook verification, refunds, chargebacks, disputes and ledger reconciliation with the payment provider.
4. Complete authenticated full order-to-delivery browser tests with custodial inventory reconciliation.
5. Obtain independent operational evidence for secrets management, audit retention, backup recovery and incident response.
6. Complete written finance/security/legal/operations approvals for any live pilot.

## Assessment structure
The code-based finance security assessment lists nine evidence gates with designated reviewers and required proof. All are initially unverified and cannot self-approve. CI only verifies the registry remains fail-closed; it does not substitute for signed governance decisions.

**Live payments, refunds, physical dispatch and external pilot remain disabled or unapproved.**
