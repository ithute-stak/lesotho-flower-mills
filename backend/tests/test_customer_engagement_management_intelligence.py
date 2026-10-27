from datetime import date
import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import engagement_management_report, router
from app.finance_permissions import finance_read

class Query:
 def __init__(self, rows): self.rows=rows
 def mappings(self): return self
 def all(self): return self.rows

class DB:
 def execute(self, statement, params):
  if "avg_turnaround_hours" in str(statement):
   return Query([{"actor":"reviewer","action":"approved","decisions":2,"avg_turnaround_hours":12.5}])
  return Query([{"month":"2026-10","action":"approved","decisions":2}])

def test_reporting_is_planning_only():
 result=engagement_management_report(start=date(2026,10,1),end=date(2026,10,27),identity={"sub":"viewer"},db=DB())
 assert result["reviewer_activity"][0]["decisions"]==2
 assert result["monthly_trends"][0]["month"]=="2026-10"
 assert result["actual_sales"] is None
 assert result["automatic_ordering_enabled"] is False

def test_invalid_range_rejected():
 with pytest.raises(HTTPException):
  engagement_management_report(start=date(2026,11,1),end=date(2026,10,1),identity={"sub":"viewer"},db=DB())

def test_finance_permission_required():
 route=next(r for r in router.routes if r.path.endswith("/reports/management"))
 assert any(d.call is finance_read for d in route.dependant.dependencies)
