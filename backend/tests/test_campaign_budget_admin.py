from fastapi import HTTPException
from pydantic import ValidationError
import pytest
from app.campaign_budget_admin import router,BudgetDraft,approve_budget
from app.finance_permissions import finance_read,finance_review,finance_admin

def test_budget_routes_require_finance_grants():
 routes={(r.path,m):r for r in router.routes for m in getattr(r,"methods",[])}
 for path,method,permission in [
  ("/api/v1/admin/campaign-budgets","POST",finance_review),
  ("/api/v1/admin/campaign-budgets","GET",finance_read),
  ("/api/v1/admin/campaign-budgets/{budget_id}/approve","POST",finance_admin)]:
  assert any(d.call is permission for d in routes[path,method].dependant.dependencies)

def test_budget_rejects_nonpositive_values():
 for value in ("0","-2"):
  with pytest.raises(ValidationError):
   BudgetDraft(campaign_id="00000000-0000-0000-0000-000000000001",limit_amount=value)

class Result:
 def __init__(self,row):self.row=row
 def mappings(self):return self
 def first(self):return self.row
class DB:
 def __init__(self,row):self.row=row;self.writes=0
 def execute(self,statement,*args,**kwargs):
  if str(statement).startswith(("UPDATE","INSERT")):self.writes+=1
  return Result(self.row)
 def commit(self):pass

@pytest.mark.parametrize("row,status",[
 (None,404),
 ({"status":"approved","created_by":"other"},409),
 ({"status":"draft","created_by":"maker"},403),
])
def test_invalid_budget_approvals_do_not_write(row,status):
 db=DB(row)
 with pytest.raises(HTTPException) as error:
  approve_budget("00000000-0000-0000-0000-000000000001",{"sub":"maker"},db)
 assert error.value.status_code==status
 assert db.writes==0
