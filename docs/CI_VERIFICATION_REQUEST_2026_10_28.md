# Verification request — 28 October 2026

Purpose: trigger the six push-to-main verification workflows against one identical commit. This document records a request, **not** a passing result or a deployment approval.

Required GitHub Actions workflows:
- CI
- Backend Browser E2E
- Deployment Config
- Docker Network Isolation
- Full Stack Network Isolation
- Release Readiness Evidence

After the push completes, inspect the Actions runs for the commit SHA, then manually invoke Consolidated Release Evidence with that SHA. A green run does not by itself authorize deployment; staging checks and explicit approvals remain required.
