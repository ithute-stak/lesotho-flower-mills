import pytest
from pydantic import ValidationError
from app.customer_engagement_admin import router,RepeatOrderDraft
from app.finance_permissions import finance_read,finance_review

ID="00000000-0000-0000-0000-000000000001"
def test_engagement_routes_restricted():
 for route in router.routes:
  expected=finance_read if "GET" in route.methods else finance_review
  assert any(dep.call is expected for dep in route.dependant.dependencies)

def test_repeat_orders_reject_invalid_frequency_and_quantity():
 for quantity,frequency in [(0,"weekly"),(10,"daily")]:
  with pytest.raises(ValidationError):
   RepeatOrderDraft(customer_id=ID,product_id=ID,quantity=quantity,frequency=frequency)

def test_no_automatic_order_execution_api():
 assert not any("execute" in route.path or "redeem" in route.path for route in router.routes)
