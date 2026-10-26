"""Machine-readable release gate summary. Never auto-approve from CI success."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ReleaseGate:
 code:str
 responsible_party:str
 evidence_required:str

RELEASE_GATES=(
 ReleaseGate("ithute_auth","Identity owner","Live signed issuer, staff MFA, current membership and revocation verification"),
 ReleaseGate("finance","Finance owner","Approved pricing/tax and payment settlement/refund reconciliation"),
 ReleaseGate("fulfilment","Operations owner","Accepted inventory custody and complete order-to-delivery UAT"),
 ReleaseGate("security","Independent reviewer","Gateway penetration review, secrets, audit retention and security sign-off"),
 ReleaseGate("operations","Deployment owner","TLS validation, monitoring, backup restore and rollback drills"),
 ReleaseGate("business","Authorised sponsor","Written customer and business pilot acceptance"),
)

def readiness_report(approved_evidence:dict|None=None)->dict:
 # Evidence submitted in code or CI is not independently verified approval.
 # Accept evidence identifiers for reporting, but never grant deployment.
 evidence=approved_evidence or {}
 return {
  "production_ready":False,
  "external_pilot_approved":False,
  "unverified":[{"code":g.code,"owner":g.responsible_party,
                 "requirement":g.evidence_required,
                 "claimed_reference":evidence.get(g.code)} for g in RELEASE_GATES],
 }
