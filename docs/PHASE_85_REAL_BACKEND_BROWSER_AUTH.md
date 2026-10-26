# Phase 85 — Isolated real-backend browser authentication

Phase 84 main CI and browser smoke passed. Added a dedicated GitHub Actions job with disposable PostgreSQL, Alembic migrations, an explicitly CI-restricted synthetic staff seed, local FastAPI, Next.js apps and Chromium Playwright. The new test signs into the warehouse portal using the real local login API, checks authenticated inventory access, signs out, and verifies an unknown user is rejected. The regular browser smoke suite skips backend-dependent tests.

These tests use synthetic credentials only and do **not** enable central Ithute Auth OAuth or validate its membership attestation. They do not execute financial transactions, shipment release, warehouse writes, or production customer activity. Real E2E job results must be green before considering the test environment verified; further role-negative, customer workflow and stock mutation tests remain outstanding.
