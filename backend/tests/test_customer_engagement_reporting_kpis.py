from datetime import date
from app.customer_engagement_admin import engagement_management_report

class Rows:
 def __init__(self,items):self.items=items
 def mappings(self):return self
 def all(self):return self.items

class DB:
 def execute(self,sql,params):
  if "avg_turnaround_hours" in str(sql):
   return Rows([{"actor":"reviewer","action":"approved","decisions":3,"avg_turnaround_hours":4},{"actor":"reviewer","action":"rejected","decisions":1,"avg_turnaround_hours":6}])
  return Rows([])

class EmptyDB:
 def execute(self,sql,params):return Rows([])

def test_management_kpis_derive_from_recorded_reviews():
 report=engagement_management_report(start=date(2026,10,1),end=date(2026,10,31),identity={"sub":"viewer"},db=DB())
 assert report["kpis"]=={"total_decisions":4,"approvals":3,"rejections":1,"approval_share_percent":75.0}
 assert report["actual_sales"] is None

def test_empty_period_does_not_invent_a_rate():
 report=engagement_management_report(identity={"sub":"viewer"},db=EmptyDB())
 assert report["kpis"]["total_decisions"]==0
 assert report["kpis"]["approval_share_percent"] is None
