# Phase 82 — Automated browser smoke tests

Added Playwright with Chromium tests for the customer and administration Next.js applications, plus a dedicated Browser Smoke GitHub Actions workflow. Each app starts on a dedicated development port in CI. The customer test checks home-to-shop navigation, prevents quote submission without published products, and navigates to registration and sign-in. The administration test confirms the unauthenticated staff sign-in screen is displayed. Failure traces are uploaded for diagnosis.

**Scope:** These are unauthenticated browser-rendering smoke tests, not completed registered-user purchases or full order-to-delivery E2E tests. They use no live payments, financial approvals, real orders or delivery activity. Browser CI and backend CI must both pass before interpreting the checks as verified. Future tests require synthetic backend fixtures, authenticated customer/staff roles, and cross-portal state verification. External pilot remains blocked.
