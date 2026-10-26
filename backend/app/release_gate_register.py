"""Release gates with evidence identifiers, never self-approving.

This read-only registry represents outstanding work. Evidence must be reviewed
in a separate controlled process before any release decision changes.
"""
from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class ReleaseGate:
    code:str
    owner:str
    evidence:str
    target:str

GATES=(
 ReleaseGate("isolated_test_data","QA","Demo environment isolation record","demo"),
 ReleaseGate("end_to_end_order_test","QA","Recorded quotation-to-delivery journey","demo"),
 ReleaseGate("no_real_transactions","Operations","Payment and dispatch feature-flag inspection","demo"),
 ReleaseGate("central_auth_e2e","Security","OIDC callback/nonce/revocation test report","pilot"),
 ReleaseGate("staff_membership_verified","Security","Identity ownership and role-removal test","pilot"),
 ReleaseGate("tax_pricing_approved","Finance","Signed price-book and tax treatment acceptance","pilot"),
 ReleaseGate("settlement_verified","Finance","Provider sandbox reconciliation and reversal evidence","pilot"),
 ReleaseGate("warehouse_custody_verified","Warehouse","Reservation/pick/dispatch custody reconciliation","pilot"),
 ReleaseGate("backup_restore_tested","Operations","Timestamped restoration drill","pilot"),
 ReleaseGate("customer_web_e2e","QA","Customer registration/cart/order browser evidence","pilot"),
 ReleaseGate("admin_web_e2e","QA","Admin pricing/finance browser evidence","pilot"),
 ReleaseGate("warehouse_web_e2e","QA","Warehouse pick/loading browser evidence","pilot"),
 ReleaseGate("driver_web_e2e","QA","Driver delivery/POD browser evidence","pilot"),
)
def release_gate_register()->list[dict]:
    return [{**asdict(g),"status":"unverified","evidence_reference":None} for g in GATES]
