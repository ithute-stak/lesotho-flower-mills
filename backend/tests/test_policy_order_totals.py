from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.policy_order_totals import discount_allowed

def test_discount_limit():
 assert discount_allowed(Decimal("2000"),Decimal("100"),500)
 assert not discount_allowed(Decimal("2000"),Decimal("100.01"),500)
 assert not discount_allowed(Decimal("2000"),Decimal("-1"),500)
def test_policy_draft_requires_auth():
 response=TestClient(app).post("/api/v1/admin/policy-order-totals/drafts",
 json={"order_id":"00000000-0000-0000-0000-000000000001",
 "policy_id":"00000000-0000-0000-0000-000000000002","method":"collection"})
 assert response.status_code==401
