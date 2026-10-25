# Phase 2 — customer and pricing domain

Implemented:
- Database foundation for customer memberships, business verification, price books, price tiers.
- Configurable fixed-bundle and volume-all-units pricing calculation, with unit tests.
- Public catalogue categories.
- Pricing **preview** API only. The caller submits all rates; never use this as a real checkout authority.

Not yet implemented:
- Account login / secure registration / verification review.
- Authorised price book lookup and customer-specific pricing.
- Product master data CRUD and product variant inventory.
- Quotations, orders, taxes, stock availability and payments.

The Makhulo M430/M2000/M3500 example is sample input supplied during planning, not an official LFM price list. Do not seed it as authoritative product prices.

An official order price must be computed exclusively by trusted backend rules using the authorised, effective price book. Product and price administration must require staff authentication, validation and audit logging.
