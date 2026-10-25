# Phase 9 — Customer quotation requests (restricted release)

Implemented:
- Explicit retail/business price-book audiences, defaulting existing books to INTERNAL to prevent accidental price exposure.
- Approved-business-only price-book assignment endpoint (staff).
- Authenticated customer-owner quotation requests without caller-supplied prices or price book IDs.
- Published retail-book fallback; eligible assigned business book preferred.
- Customer quotation listing scoped by membership.

Important limitations:
- No price book audience administration UI; existing books remain internal until staff securely configure them.
- Multiple simultaneously published retail books or assigned business books cause an explicit conflict, rather than an arbitrary selection.
- Only single-account owners supported; company purchasing permissions and business approvals need extension.
- Generated quotations remain DRAFT and omit tax, freight, stock checking and issuance.
- No checkout, orders or inventory reservations yet. Never call this production-ready.
