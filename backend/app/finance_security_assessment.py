"""Fail-closed finance security sign-off checklist; no self-certification."""
from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class FinanceSecurityGate:
 code:str
 reviewer:str
 evidence:str

GATES=(
 FinanceSecurityGate("finance_role_matrix","Independent security reviewer","Role matrix and latest CI test references"),
 FinanceSecurityGate("maker_checker","Finance control owner","Independent approval and revocation test evidence"),
 FinanceSecurityGate("identity_attestation","Identity security owner","Ithute Auth issuer, audience, membership and revocation E2E"),
 FinanceSecurityGate("payment_settlement","Finance and payment partner","Provider-signed settlement and reconciliation evidence"),
 FinanceSecurityGate("refund_reversal","Finance and payment partner","Refund, reversal and dispute reconciliation tests"),
 FinanceSecurityGate("tax_delivery_pricing","Commercial finance owner","Approved tax, discounts and delivery-fee policy"),
 FinanceSecurityGate("secrets_and_audit","Infrastructure security owner","Secret rotation, audit export and retention review"),
 FinanceSecurityGate("backup_incident","Operations owner","Restore drill and incident-response exercise"),
 FinanceSecurityGate("independent_signoff","Authorised governance approver","Signed security decision and remediation register"),
)

def finance_security_assessment():
 return {"approved":False,"external_pilot_allowed":False,
         "gates":[{**asdict(g),"status":"unverified","reviewed_by":None,
                   "evidence_reference":None} for g in GATES]}
