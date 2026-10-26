# Phase 64 — Central staff identity binding

Added an explicit identity mapping from (Ithute Auth issuer, central subject) to an active local LFM user, with unique mappings and an activation constraint requiring verification metadata. All records start inactive. The resolver checks both the binding and current local account active/staff status on each call; it never grants staff access based solely on remote token claims.

The resolver is **not yet wired into the live authentication dependency**. No binding-admin UI or secure onboarding/attestation workflow exists, so no mappings are automatically activated. Central session verification must precede membership lookup; finance access must also check current finance grants against the resolved local subject. Production approval requires audit-protected binding administration, central session tests and end-to-end login tests.

Phase 63 admin-web CI type error was addressed separately in this phase.
