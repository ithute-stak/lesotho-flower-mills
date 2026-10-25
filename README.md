# Lesotho Flour Mills Commerce & Distribution

Phase 1 foundation for a hybrid B2C/B2B sales, inventory and delivery platform.

## Local setup

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build -d`.
3. Open API docs at http://localhost:8000/docs and the customer starter at http://localhost:3000.
4. Health: `curl http://localhost:8000/health`
5. Run backend tests: `docker compose exec api pytest -q`.

This is **not production-ready**. Products/prices require LFM verification; payment, stock reservation and delivery confirmations will be implemented in later phases. No demonstration price should be treated as LFM's current selling price.

Architecture: FastAPI, PostgreSQL/Alembic, Next.js, Docker. Each domain will own its data model and business rules. Inventory and payment effects must use atomic transactions and idempotency.
