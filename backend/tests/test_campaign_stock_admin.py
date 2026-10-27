from fastapi import HTTPException
import pytest
from app.campaign_stock_admin import StockPlan,create_stock_plan,router
from app.finance_permissions import finance_read,finance_review

UID="00000000-0000-0000-0000-000000000001"
def test_stock_plan_routes_are_finance_restricted():
 paths={(route.path,m):route for route in router.routes for m in getattr(route,"methods",[])}
 for path,method,dep in [
  ("/api/v1/admin/campaign-stock","POST",finance_review),
  ("/api/v1/admin/campaign-stock","GET",finance_read)]:
  assert any(d.call is dep for d in paths[path,method].dependant.dependencies)

class Result:
 def __init__(self,value):self.value=value
 def mappings(self):return self
 def first(self):return self.value
class DB:
 def __init__(self,values):self.values=iter(values);self.writes=0
 def execute(self,query,*args,**kwargs):
  if str(query).startswith("INSERT"):self.writes+=1
  return Result(next(self.values,None))
 def commit(self):pass

@pytest.mark.parametrize("rows,status",[
 ([None],404),
 ([{"status":"disabled"}],409),
 ([{"status":"approved"},None],409),
 ([{"status":"approved"},{"on_hand":15,"reserved":10}],409),
])
def test_stock_plans_fail_closed_without_inventory(rows,status):
 db=DB(rows)
 body=StockPlan(campaign_id=UID,warehouse_id=UID,product_id=UID,planned_quantity=6)
 with pytest.raises(HTTPException) as err:
  create_stock_plan(body,{"sub":"reviewer"},db)
 assert err.value.status_code==status
 assert db.writes==0
