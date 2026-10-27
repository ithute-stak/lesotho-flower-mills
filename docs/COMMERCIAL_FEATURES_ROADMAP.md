# Commercial Features Roadmap — Lesotho Flour Mills

## Release order

1. **Promotions foundation (in progress).** Deterministic quote preview, approved server-owned campaigns, one discount at a time, capped discounts and customer eligibility. The initial engine is a pure library only. No discounts are applied to checkout or official order totals.
2. **Promotion persistence and approvals.** PostgreSQL migrations, campaign status workflow, finance role checks, maker/checker, row locking, effective date/version checks, stock limits, budget caps, audit events and idempotent redemption records. Do not accept client-provided approval flags.
3. **Wholesale pricing.** Approved customer price lists, tiered pricing, negotiated contracts, net-of-discount controls and signed price snapshots.
4. **Customer engagement.** Loyalty, coupon codes, opt-in notifications, subscriptions/reorders, referrals and campaign budget reporting.
5. **Field sales and distribution.** Territory assignment, visits, order capture, claims/returns and customer account visibility.
6. **Analytics.** Campaign ROI, stock-aware promotions and demand forecasts with traceable source data.

## Invariants

- Finance-specific roles and independent approval for any commercial pricing effect.
- All payable totals remain blocked by existing external policy, tax, tariff, settlement and staff verification gates.
- No coupon redemption or stock reservation merely because a preview succeeds.
- Customer groups come from approved backend membership, not browser-supplied identities.
- Revenue-impacting campaign changes require logs, versioned pricing snapshots and reconciliation tests.

## Current delivery

`backend/app/promotions_engine.py` and `backend/tests/test_promotions_engine.py` provide a standalone *draft-only* promotion quote implementation and negative tests. It is not yet wired into the API or web applications.
