from app.wholesale_promotion_reports import router,wholesale_promotion_summary
from app.finance_permissions import finance_read

def test_wholesale_reports_are_finance_protected():
 for route in router.routes:
  assert any(dep.call is finance_read for dep in route.dependant.dependencies)

class Query:
 def mappings(self):return self
 def all(self):return [{"status":"approved","tier_count":2,"campaign_count":1,
 "product_count":2,"minimum_quantity":10,"maximum_quantity":100}]
class DB:
 def execute(self,*args,**kwargs):return Query()

def test_summary_does_not_claim_redeemed_discounts():
 result=wholesale_promotion_summary({"sub":"auditor"},DB())
 assert result["basis"]=="administrative_plans_only"
 assert result["checkout_enabled"] is False
 assert result["total_tiers"]==2
 assert result["actual_discount_amount"] is None
 assert result["actual_incremental_revenue"] is None
