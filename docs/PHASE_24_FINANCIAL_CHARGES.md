# Phase 24 — Financial charges and order totals groundwork

Implemented an isolated Decimal calculator for subtotal, discount, delivery fee, optionally taxable freight, basis-point tax rate, tax amount and gross total with half-up cent rounding. Added an order-linked finance.order_totals schema and staff-only preview endpoint. No authority is granted to customer-supplied amounts.

Important: preview input (tax rate, taxability, discount and freight) is staff-supplied **for modelling only**, not validated against Lesotho tax law, approved policy or delivery zones. The schema stores proposed fields but no endpoint approves/finalises a total yet. Finance controls intentionally remain fail closed.

Before launch, define approved effective-dated tax codes, tax-inclusive vs tax-exclusive prices, exempt goods, transport tax treatment, delivery zone calculations, discount approvals and immutable policy version references. Freeze final payable total transactionally and switch IthutePay initiation to that total (not order subtotal). Reconcile payments to full gross total before enabling confirmed orders. Never rely on these previews as tax advice or issued invoices.
