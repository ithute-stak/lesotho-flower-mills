from fastapi import HTTPException
import pytest
from app.campaign_admin import router,disable_campaign
from app.finance_permissions import finance_admin,finance_read

def test_disable_and_audit_endpoints_require_finance_grants():
 routes={(route.path,method):route for route in router.routes for method in getattr(route,"methods",[])}
 for path,method,permission in [
  ("/api/v1/admin/campaigns/{campaign_id}/disable","POST",finance_admin),
  ("/api/v1/admin/campaigns/{campaign_id}/events","GET",finance_read),
 ]:
  assert any(dep.call is permission for dep in routes[(path,method)].dependant.dependencies)

class Result:
 def __init__(self,row):self.row=row
 def mappings(self):return self
 def first(self):return self.row
class DB:
 def __init__(self,row):self.row=row;self.writes=0
 def execute(self,statement,*args,**kwargs):
  if str(statement).startswith("UPDATE ") or str(statement).startswith("INSERT "):self.writes+=1
  return Result(self.row)
 def commit(self):pass

def test_campaign_cannot_be_disabled_twice():
 db=DB({"status":"disabled"})
 with pytest.raises(HTTPException) as exc:
  disable_campaign("00000000-0000-0000-0000-000000000001",{"sub":"finance-admin"},db)
 assert exc.value.status_code==409
 assert db.writes==0

def test_missing_campaign_does_not_create_event():
 db=DB(None)
 with pytest.raises(HTTPException) as exc:
  disable_campaign("00000000-0000-0000-0000-000000000001",{"sub":"finance-admin"},db)
 assert exc.value.status_code==404
 assert db.writes==0
