from fastapi import HTTPException
import pytest
from pydantic import ValidationError
from app.wholesale_promotion_admin import router,WholesaleTierDraft,create_wholesale_tier,approve_wholesale_tier
from app.finance_permissions import finance_read,finance_review,finance_admin
ID="00000000-0000-0000-0000-000000000001"
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

def test_wholesale_permissions():
 routes={(r.path,m):r for r in router.routes for m in getattr(r,"methods",[])}
 for path,method,dep in [
  ("/api/v1/admin/wholesale-promotions","POST",finance_review),
  ("/api/v1/admin/wholesale-promotions","GET",finance_read),
  ("/api/v1/admin/wholesale-promotions/{tier_id}/approve","POST",finance_admin)]:
  assert any(d.call is dep for d in routes[path,method].dependant.dependencies)

def test_invalid_quantities_rejected():
 with pytest.raises(ValidationError):
  WholesaleTierDraft(campaign_id=ID,product_id=ID,minimum_quantity=1,discount_bps=100)

def test_public_campaign_rejected_without_writes():
 db=DB({"status":"approved","audience":"public"})
 with pytest.raises(HTTPException) as err:
  create_wholesale_tier(WholesaleTierDraft(campaign_id=ID,product_id=ID,minimum_quantity=10,discount_bps=500),{"sub":"maker"},db)
 assert err.value.status_code==409 and db.writes==0

def test_self_approval_rejected_without_writes():
 db=DB({"status":"draft","created_by":"maker","campaign_status":"approved","audience":"business"})
 with pytest.raises(HTTPException) as err:approve_wholesale_tier(ID,{"sub":"maker"},db)
 assert err.value.status_code==403 and db.writes==0
