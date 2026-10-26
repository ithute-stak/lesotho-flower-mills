"""Conservative readiness checklist; not a deployment authorization."""
REQUIRED_DEMO=("isolated_test_data","end_to_end_order_test","no_real_transactions")
REQUIRED_PILOT=("central_auth_e2e","staff_membership_verified","tax_pricing_approved",
 "settlement_verified","warehouse_custody_verified","backup_restore_tested")
def assess_pilot_readiness():
    """No independent evidence registry exists; never self-certify readiness."""
    return {"demo_ready":False,"external_pilot_ready":False,
            "production_ready":False,
            "missing_demo_evidence":list(REQUIRED_DEMO),
            "missing_pilot_evidence":list(REQUIRED_PILOT)}
