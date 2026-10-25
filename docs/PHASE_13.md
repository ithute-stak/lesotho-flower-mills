# Phase 13 — Warehouse picking and loading

Added:
- Pick list creation from confirmed orders with active stock reservations.
- Full-quantity picking and loading checks with row locking.
- Driver and vehicle details captured with verified loading manifest.
- Duplicate pick lists/loading manifests rejected.
- No stock dispatch endpoint yet; payment and credit confirmation remain unimplemented.

**Important:** This phase is designed to fail closed: orders from earlier phases remain pending_payment and therefore cannot be picked or loaded. Warehouse stock is not deducted or reservation consumed until an independently verified dispatch process is built. This is not an operational dispatch system yet.
