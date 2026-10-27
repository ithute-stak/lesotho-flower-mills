from fastapi import HTTPException
import pytest
from pydantic import ValidationError
from app.coupon_admin import router,NewCoupon,create_coupon,disable_coupon
from app.finance_permissions import finance_read,finance_review,finance_admin

ID="00000000-0000-0000-0000-000000000001"

class Result:
 def __init__(self,row):self.row=row
 def mappings(self):return self
 def first(self):return self.row
class DB:
 def __init__(self,row):self.row=row;self.writes=0
 def execute(self,query,*args,**kwargs):
  if str(query).startswith(("INSERT","UPDATE")):self.writes+=1
  return Result(self.row)
 def commit(self):pass

def test_coupon_routes_have_finance_grants_and_no_redemption():
 paths={(route.path,method):route for route in router.routes for method in getattr(route,"methods",[])}
 for path,method,dep in [
  ("/api/v1/admin/coupons","POST",finance_review),
  ("/api/v1/admin/coupons","GET",finance_read),
  ("/api/v1/admin/coupons/{coupon_id}/disable","POST",finance_admin)]:
  assert any(d.call is dep for d in paths[(path,method)].dependant.dependencies)
 assert not any("redeem" in path for path,_ in paths)

def test_disallowed_coupon_codes_and_limits():
 with pytest.raises(ValidationError):
  NewCoupon(campaign_id=ID,code="bad code",max_redemptions=10)
 with pytest.raises(ValidationError):
  NewCoupon(campaign_id=ID,code="GOOD",max_redemptions=0)

def test_disabled_campaign_rejects_coupon_creation():
 db=DB({"status":"disabled"})
 with pytest.raises(HTTPException) as err:
  create_coupon(NewCoupon(campaign_id=ID,code="SAVE25",max_redemptions=50),{"sub":"maker"},db)
 assert err.value.status_code==409
 assert db.writes==0

def test_disabled_coupon_cannot_be_disabled_again():
 db=DB({"status":"disabled"})
 with pytest.raises(HTTPException) as err:
  disable_coupon(ID,{"sub":"admin"},db)
 assert err.value.status_code==409
 assert db.writes==0
