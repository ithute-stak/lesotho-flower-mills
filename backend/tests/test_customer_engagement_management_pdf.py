from datetime import date
import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import engagement_management_pdf, router
from app.finance_permissions import finance_read

class Rows:
 def __init__(self,values):self.values=values
 def mappings(self):return self
 def all(self):return self.values

class DB:
 def execute(self,sql,params):
  if "avg_turnaround_hours" in str(sql):
   return Rows([{"actor":"Reviewer A","action":"approved","decisions":2,"avg_turnaround_hours":12.5}])
  return Rows([{"month":"2026-10","action":"approved","decisions":2}])

def test_pdf_header_and_content():
 result=engagement_management_pdf(start=date(2026,10,1),end=date(2026,10,31),identity={"sub":"viewer"},db=DB())
 assert result.media_type=="application/pdf"
 assert result.body.startswith(b"%PDF")
 assert len(result.body)>1000
 assert "attachment;" in result.headers["content-disposition"]
 assert result.headers["cache-control"]=="no-store"

def test_pdf_rejects_invalid_range():
 with pytest.raises(HTTPException) as exc:
  engagement_management_pdf(start=date(2026,11,1),end=date(2026,10,1),identity={"sub":"viewer"},db=DB())
 assert exc.value.status_code==422

def test_finance_permission_on_pdf_route():
 routes=[r for r in router.routes if r.path.endswith("/reports/management.pdf")]
 assert len(routes)==1
 assert any(dep.call is finance_read for dep in routes[0].dependant.dependencies)
