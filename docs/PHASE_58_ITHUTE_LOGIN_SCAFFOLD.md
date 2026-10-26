# Phase 58 — Central login scaffold (disabled by default)

The admin web app now has server-only Ithute Auth configuration preflight and routes at `/api/auth/ithute/status`, `/api/auth/ithute/login`, `/api/auth/ithute/callback`, and `POST /api/auth/ithute/logout`.

These routes deliberately do **not** exchange OAuth codes, issue sessions, store tokens or redirect users. Login/callback/logout return 503 pending verified registration and a vetted implementation of PKCE state, nonce, callback CSRF protection, encrypted HttpOnly cookie sessions and online session revocation. The status route returns blockers without secrets, and is not proof of production readiness.

The upstream Ithute Next.js SDK is not yet published; no new npm dependency was installed. Existing local LFM login, finance role checks, and blocked payment approvals remain unchanged. To activate, register the LFM client with exact HTTPS callback, verify real discovery and session endpoints, add browser E2E tests, and perform a security review.
