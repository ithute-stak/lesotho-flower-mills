# Phase 67 — Central identity attestation safeguards

Phase 66 CI passed. Added a fail-closed attestation policy for future central Ithute Auth integration, comparing the verified central issuer and subject against the proposed staff link, and requiring an active verified central session. Unit tests cover wrong issuer, wrong subject and revoked session.

**Not a completed ownership ceremony:** The policy deliberately has no admin-facing endpoint and does not write the attestation database fields. The secure, authenticated Ithute session-to-LFM linking ceremony and central attestations remain to be built and verified. Therefore staff-link activation remains blocked. PostgreSQL integration and competing-review transaction tests remain outstanding; no payment controls were loosened.
