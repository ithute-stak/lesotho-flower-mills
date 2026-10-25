# Phase 19 — Customer acknowledgement, disputes, shared Ithute services

## LFM-specific responsibilities
LFM owns its sales catalogue, quantity pricing, warehouse stock ledger, stock reservations, picking/loading, deliveries, goods-received evidence, discrepancies and dispute resolution.

## Shared Ithute services to evaluate
- **Ithute Auth:** central identity, user sessions, MFA and scoped service permissions. Use a trusted OIDC/OAuth2 flow only after exact issuer, audience, JWKS and revocation semantics are established. Do not share signing secrets across systems.
- **IthutePay:** provider integrations, secure checkout, webhook validation, settlement/reconciliation and refunds. LFM should consume verified provider-neutral settlement events, never accept browser success claims.
- **Ithute document service:** quotations, invoices, manifests and proof-of-delivery PDFs, with versioned templates and audit metadata. Keep snapshot data and document identifiers in LFM.
- **Ithute notifications:** SMS/email delivery OTPs and transactional order updates, with consent, retry policy and delivery receipts.
- **Ithute infrastructure:** central observability, audit correlation IDs, deployment and backups where supported.

**No live Ithute integration has been assumed or claimed.** Inspect the actual Ithute interfaces and credentials before implementing adapters.

## Phase 19 delivery
- Customer-owned, single-use acknowledgement endpoint, restricted to an arrived delivery with previously verified handover code.
- Partial/rejected deliveries create line-level discrepancy evidence and open a dispute automatically.
- Acceptance is recorded but does not mark the delivery completed, consume inventory or trigger funds release.
- Full proof-of-delivery documents, recipient identity validation, signatures and exception handling are future work.
