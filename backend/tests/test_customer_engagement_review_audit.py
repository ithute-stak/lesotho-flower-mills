from datetime import date
import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import _audit_rows,engagement_review_audit,engagement_review_audit_csv,router
from app.finance_permissions import finance_read

class Result:
 def mappings(self):return self
 def all(self):return []

class DB:
 def __init__(self):self.query=None;self.params=None
 def execute(self,statement,params):self.query=str(statement);self.params=params;return Result()

def test_filtered_audit_is_bounded_and_parameterized():
 db=DB()
 result=engagement_review_audit(status="approved",actor="finance-reviewer",start=date(2026,10,1),
 end=date(2026,10,27),limit=10,offset=20,identity={"sub":"viewer"},db=db)
 assert result["basis"]=="planning_only" and result["items"]==[]
 assert db.params["actor"]=="finance-reviewer" and db.params["limit"]==10
 assert ":actor" in db.query and ":status" in db.query
 assert "ORDER BY" in db.query

def test_bad_date_range_and_status_blocked():
 db=DB()
 with pytest.raises(HTTPException) as error:
  _audit_rows(db,None,None,date(2026,11,1),date(2026,10,1),100,0)
 assert error.value.status_code==422
 with pytest.raises(HTTPException):
  _audit_rows(db,"activated",None,None,None,100,0)

def test_csv_export_header_and_no_financial_claim():
 response=engagement_review_audit_csv(identity={"sub":"viewer"},db=DB())
 assert b"PLANNING ONLY" in response.body
 assert b"template_id" in response.body
 assert "attachment;" in response.headers["content-disposition"]

def test_all_audit_routes_require_finance_access():
 routes=[r for r in router.routes if "/reports/review-audit" in r.path]
 assert len(routes)==2
 for route in routes:
  assert any(dep.call is finance_read for dep in route.dependant.dependencies)
