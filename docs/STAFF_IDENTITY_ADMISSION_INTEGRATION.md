# Staff identity admission integration

All six latest CI workflows passed before this change. This change composes token verification with the existing nine-condition admission policy and adds tests for every missing independent staff attestation.

**This is not a production staff gateway.** StaffAttestation values are currently provided by trusted test code only: no live provider verifies membership, MFA, revocation, gateway deployment or independent approval. Do not construct these booleans from untrusted claims or request headers. No public admin/warehouse routes have been enabled, and live payments, refunds, dispatch and pilot approval remain blocked.
