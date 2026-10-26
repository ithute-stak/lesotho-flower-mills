# Staff evidence provider boundary

Verified previous main CI, Backend Browser E2E, Full Stack Network Isolation, Docker Network Isolation and Deployment Config passed. Added a staff evidence provider interface with fail-closed behaviour when no approved provider exists, independent subject matching, active membership, MFA and current-session requirements. Unit tests include valid synthetic data and all denial scenarios.

**Important:** The provider interface is not a live Ithute Auth integration. The success test injects synthetic evidence; no network provider, staff gateway route or public portal access has been enabled. Provider evidence must be obtained over approved secure authenticated server-to-server integration with verified freshness, organisation scope and revocation policies. Gateway deployment and security approval still block production access. Payments, refunds, dispatch and external pilot remain disabled or unapproved.
