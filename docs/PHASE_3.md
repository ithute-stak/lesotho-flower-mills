# Phase 3: account and catalogue foundations

Implemented:
- Argon2id password hashing and 30-minute signed JWT access tokens.
- Individual/business self-registration (always customer role).
- Email/password login, /account/me, staff-only business approval.
- Database-backed product listing, restricted product creation, inactive price book creation.
- Identity schema migration and unit/API security tests.

Security and operational limitations:
- No public staff provisioning endpoint. Privileged identities require a separate controlled provisioning process not yet implemented.
- Self-registration is not equivalent to verified email/phone or approved business status.
- Business approval currently records status only: expand to evidence review, reviewer, audit events, and dual control before production.
- No token refresh, rate limiting, password reset, MFA, email verification, customer notification or production secret management yet.
- No price book activation, tier management or trusted price calculation yet.
- No real orders, reservations, payments or delivery functionality yet.
- Do NOT deploy to production without the above controls and transaction/audit verification.
