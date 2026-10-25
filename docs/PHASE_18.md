# Phase 18 — Proof of delivery foundation

Added immutable-style handover event records, scoped 6-digit challenge hash verification, expiry checks, five-attempt limit, single-use consumption and driver identity checks.

**Not live:** OTP challenge issuance and delivery-completion/customer-acknowledgement endpoints are deliberately unavailable. These require independently verified dispatch, recipient identity validation, customer consent, signature/receipt capture, partial-delivery and discrepancy handling, secure challenge delivery, and staff review.

No code is ever returned from an unauthenticated API. Verification of a code does not mark goods delivered. Keep the POD_HMAC_SECRET confidential (>=32 chars) when the service is eventually activated.
