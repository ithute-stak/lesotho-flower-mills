from fastapi import HTTPException
import pytest
from app.wholesale_promotion_admin import router,disable_wholesale_tier
from app.finance_permissions import finance_read,finance_admin
def test_wholesale_lifecycle_grants():
 routes={(r.path,m):r for r in router.routes for m in getattr(r,"methods",[])}
 for path,method,dep in [
 ("/api/v1/admin/wholesale-promotions/{tier_id}/disable","POST",finance_admin),
 ("/api/v1/admin/wholesale-promotions/{tier_id}/events","GET",finance_read)]:
  assert any(x.call is dep for x in routes[path,method].dependant.dependencies)
class Result:
 def __init__(self,row):self.row=row
 def mappings(self):return self
 def first(self):return self.row
class DB:
 def __init__(self,row):self.row=row;self.writes=0
 def execute(self,q,*args,**kwargs):
  if str(q).startswith(("INSERT","UPDATE")):self.writes+=1
  return Result(self.row)
 def commit(self):pass
@pytest.mark.parametrize("row,status",[(None,404),({"status":"disabled"},409)])
def test_disabled_or_missing_tier_has_no_mutation(row,status):
 db=DB(row)
 with pytest.raises(HTTPException) as exc:
  disable_wholesale_tier("00000000-0000-0000-0000-000000000001",{"sub":"admin"},db)
 assert exc.value.status_code==status
 assert db.writes==0
