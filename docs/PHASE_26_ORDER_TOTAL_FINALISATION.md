# Phase 26 — Order total review and checkout safety

Added finance.order_totals review_status, created_by and approved_at fields with a DB trigger preventing modifications/deletion to approved rows; introduced staff-only draft-total save/read APIs. Drafts use deterministic Decimal order totals and LFM order subtotals, but tax/discount/delivery inputs are still staff-supplied and **not legally or commercially approved**. No endpoint can approve a total. No checkout should use a draft.

Checkout initiation now requires an independently approved stored gross total, rejects subtotal-only charging, and still requires an explicitly enabled IthutePay adapter.

Outstanding: independently approved effective-dated tax rules, delivery zone tariff binding, discount policy, maker/checker approval under centrally verified staff identity, database concurrency/integration tests, immutable invoice and ledger snapshots, provider settlement verification. Never bypass these controls to force a paid/confirmed order.
