# Phase 11 — Warehouse operations first slice

Adds staff-restricted, transactional stock receipts, manual adjustments, inter-warehouse transfers and a movement journal, with operation keys to reject duplicate posts.

Important: Not production ready. Warehouse-specific privileges, verified goods-received notes, adjustment maker/checker approval, immutable database permissions, reservation release/cancel, movement/stock reconciliation and real PostgreSQL concurrency tests are outstanding. The journal is append-only at API level, but database privileges must prevent direct updates/deletes.

Stock quantities currently represent whole units only. Audit movement history must be paired with production-grade roles and review controls before enabling real stock postings.
