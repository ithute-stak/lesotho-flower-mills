# Phase 25 — Transport zones and tariff pricing

Added configurable zone/tariff tables and a staff-only delivery fee preview.
- Zones default to inactive; tariffs default to unapproved.
- Effective windows and tariff versions are recorded.
- Missing or overlapping approved tariffs fail closed.
- Customer collection has zero transport fee; delivery requires a configured active zone.
- Optional threshold supports free delivery. Prices are calculated on order subtotal; discounts, product weights and tax treatment are not yet incorporated.

No real zone prices have been fabricated, no tariff approval endpoint exists and pricing is **not applied to payable orders**. LFM management must approve delivery zones, exact effective-dated rates, zone coverage and collection locations. Add transport tariff approval controls, final order price locking, combined tax basis and IthutePay charge against the locked gross total before live checkout.
