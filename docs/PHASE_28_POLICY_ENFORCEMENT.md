# Phase 28 — Financial policy enforcement on draft order totals

Added a staff-restricted policy-bound order draft endpoint. It uses only approved effective financial policies, checks maximum discount basis points, derives delivery fees from exactly one active approved zone tariff, and calculates amounts with Decimal. Customer collection uses zero freight. The draft records the policy and tariff reference and remains unapproved/not payable.

This does not enable gross-total approval or payment. Existing preview/draft APIs remain for modelling but cannot approve totals. Current staff JWT role checks are not sufficient for real financial sign-off, and policy approval is not confirmation of legal tax treatment. Additional requirements: explicit tax product classifications, policy validity periods, immutable tariff and line snapshots, version-aware maker/checker approval, independent credit policy, concurrency tests and safe migration to centrally verified Ithute Auth.
