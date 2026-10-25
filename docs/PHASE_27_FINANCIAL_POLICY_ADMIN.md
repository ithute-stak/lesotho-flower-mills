# Phase 27 — Controlled financial policy records

Adds versioned finance.financial_policies with draft/approved/rejected statuses, tax-rate basis points, delivery-tax treatment and maximum discount basis points. A staff identity may draft; a **different staff subject** must approve. PostgreSQL constraints enforce separation and prevent changes/deletions to approved policies.

Approval records administrative endorsement, **not verification of tax legislation** or automatic permission to charge. These rules are not yet connected to finance.order_totals, delivery tariffs or payable invoices. No order-total approval endpoint has been enabled. Staff role separation is limited by the current LFM JWT model; central Ithute Auth and live staff-role validation remain prerequisite for production.

Next requirements: bind each order draft to an approved, effective policy version; check discount policy, zone tariffs, tax exemptions and inclusive pricing; require independent maker-checker approval of each final order total; enforce unique effective policy selection and test PostgreSQL concurrency. No real payment/dispatch until all checks pass.
