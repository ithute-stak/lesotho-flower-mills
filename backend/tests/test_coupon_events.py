from fastapi import HTTPException
import pytest
from app.coupon_admin import router,coupon_events
from app.finance_permissions import finance_read

def test_coupon_audit_endpoint_requires_finance_read():
 route=next(r for r in router.routes if r.path=="/api/v1/admin/coupons/{coupon_id}/events")
 assert any(d.call is finance_read for d in route.dependant.dependencies)

class Result:
 def mappings(self):return self
 def first(self):return None
class DB:
 def execute(self,*args,**kwargs):return Result()

def test_coupon_audit_missing_coupon_is_404():
 with pytest.raises(HTTPException) as exc:
  coupon_events("00000000-0000-0000-0000-000000000001",{"sub":"auditor"},DB())
 assert exc.value.status_code==404
