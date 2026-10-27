from app.customer_engagement_admin import router, engagement_planning_report
from app.finance_permissions import finance_read

class Rows:
 def __init__(self,rows):self.rows=rows
 def mappings(self):return self
 def all(self):return self.rows
 def scalar_one(self):return self.rows[0]

class DB:
 def __init__(self):self.statements=[]
 def execute(self,statement):
  sql=str(statement)
  self.statements.append(sql)
  if "GROUP BY frequency,status" in sql:
   return Rows([{"frequency":"weekly","status":"draft","template_count":2,"planned_quantity_per_cycle":50}])
  if "GROUP BY referrer_customer_id" in sql:
   return Rows([{"referrer_customer_id":"00000000-0000-0000-0000-000000000001","referral_count":3}])
  return Rows([4])

def test_engagement_planning_reports_are_nonfinancial():
 db=DB()
 report=engagement_planning_report({"sub":"finance-viewer"},db)
 assert report["basis"]=="planning_only"
 assert report["actual_repeat_orders"] is None
 assert report["actual_retention_rate"] is None
 assert report["actual_referral_conversions"] is None
 assert report["actual_revenue"] is None
 assert report["repeat_order_frequency_breakdown"][0]["planned_quantity_per_cycle"]==50
 assert report["top_referrers"][0]["referral_count"]==3
 assert report["automatic_ordering_enabled"] is False
 assert report["points_enabled"] is False
 assert report["referral_rewards_enabled"] is False

def test_report_requires_finance_read():
 matches=[r for r in router.routes if r.path.endswith("/reports/planning")]
 assert len(matches)==1
 assert matches[0].methods=={"GET"}
 assert any(d.call is finance_read for d in matches[0].dependant.dependencies)
