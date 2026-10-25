"""Pure financial readiness checks; no automated settlement or dispatch authority."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping,Any

@dataclass(frozen=True)
class FinancialReadiness:
    ready:bool
    blockers:tuple[str,...]

def assess(order:Mapping[str,Any],total:Mapping[str,Any]|None,policy:Mapping[str,Any]|None,
           checkout:Mapping[str,Any]|None=None)->FinancialReadiness:
    blockers=[]
    if order.get("status")!="pending_payment":blockers.append("order_not_awaiting_payment")
    if total is None or total.get("review_status")!="approved":
        blockers.append("gross_total_not_approved")
    else:
        if Decimal(str(total.get("total",0)))<=0:blockers.append("gross_total_invalid")
        if total.get("currency")!="LSL":blockers.append("currency_not_supported")
    if policy is None or policy.get("status")!="approved":
        blockers.append("financial_policy_not_approved")
    # Approval of tax inputs does not imply they are compliant, and no provider
    # settlement/stock reconciliation checks have been implemented.
    blockers.extend(("tax_and_delivery_policy_certification_pending",
                     "ithutepay_settlement_verification_pending",
                     "stock_custody_reconciliation_pending",
                     "central_staff_role_verification_pending"))
    if checkout is not None and total is not None:
        if Decimal(str(checkout.get("amount",0)))!=Decimal(str(total.get("total",0))):
            blockers.append("checkout_amount_mismatch")
        if checkout.get("currency")!=total.get("currency"):
            blockers.append("checkout_currency_mismatch")
    return FinancialReadiness(ready=not blockers,blockers=tuple(blockers))
