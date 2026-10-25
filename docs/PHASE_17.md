# Phase 17 — Driver mobile web portal

- Driver-specific, authenticated, read-only delivery assignments.
- Active driver identity is mapped by signed JWT subject, not provided by the caller.
- Mobile-first driver web application with fixed bottom navigation and account section.
- Driver app is packaged as another Next.js container on port 3003.
- No driver-controlled dispatch, delivery completion, GPS capture or customer verification yet.
- Tokens held only in browser memory (lost on reload); production needs secure session handling, revocation, MFA and role verification.
