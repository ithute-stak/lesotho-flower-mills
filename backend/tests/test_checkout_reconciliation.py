from fastapi.testclient import TestClient
from app.main import app

def test_checkout_requires_auth():
 c=TestClient(app)
 assert c.post("/api/v1/admin/ithute-pay/checkouts",json={"order_id":"00000000-0000-0000-0000-000000000001"}).status_code==401
 assert c.post("/api/v1/admin/ithute-pay/checkouts/00000000-0000-0000-0000-000000000001/refresh").status_code==401
