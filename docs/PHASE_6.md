# Phase 6 — Pricing publication foundation

Added:
- Approved/published price book transitions and event history.
- Two-person review/publication policy (different token subjects).
- Authenticated price quote from database-backed published book; callers cannot submit price values.
- Access-control tests for pricing lifecycle and no-auth rejection.

Limitations and follow-up:
- No published-price shopping-cart/quotation integration yet.
- Book-wide publication does not yet restrict competing published books by channel/date or enforce customer price-book assignment.
- No contract pricing or effective-dated publication.
- Staff token role is currently encoded at issue time, not checked against a live persisted staff role on every request.
- No production readiness; phase is an incremental foundation.
