"""Declared finance route access requirements, enforced by regression tests."""
from dataclasses import dataclass

@dataclass(frozen=True)
class FinanceRoute:
    module:str
    function:str
    permission:str

FINANCE_ROUTES=(
 FinanceRoute("financial_policy_admin","create_policy","finance_review"),
 FinanceRoute("financial_policy_admin","approve_policy","finance_admin"),
 FinanceRoute("financial_policy_admin","list_policies","finance_read"),
 FinanceRoute("payment_authorisation","record_payment","finance_review"),
 FinanceRoute("payment_authorisation","order_payments","finance_read"),
 FinanceRoute("payment_authorisation","confirm_paid_order","finance_admin"),
 FinanceRoute("checkout_reconciliation","start_checkout","finance_review"),
 FinanceRoute("checkout_reconciliation","checkout_attempt","finance_read"),
 FinanceRoute("checkout_reconciliation","refresh_checkout","finance_review"),
 FinanceRoute("order_total_review","save_draft","finance_review"),
 FinanceRoute("order_total_review","get_total","finance_read"),
 FinanceRoute("order_totals","preview","finance_read"),
 FinanceRoute("payment_gateway","initiate","finance_review"),
 FinanceRoute("payment_gateway","providers","finance_read"),
 FinanceRoute("finance_role_admin","request_grant","finance_admin"),
 FinanceRoute("finance_role_admin","approve_grant","finance_admin"),
 FinanceRoute("finance_role_admin","revoke_grant","finance_admin"),
 FinanceRoute("finance_role_admin","grants","finance_admin"),
 FinanceRoute("finance_role_admin","audit_events","finance_admin"),
 FinanceRoute("orders","cancel_unpaid_order","finance_admin"),
 FinanceRoute("reconciliation_review","queue","finance_read"),
 FinanceRoute("reconciliation_review","history","finance_read"),
 FinanceRoute("reconciliation_review","health","finance_read"),
 FinanceRoute("reconciliation_review","alerts","finance_read"),
 FinanceRoute("reconciliation_review","email_deliveries","finance_read"),
)
