from fastapi.testclient import TestClient
from app.main import app
def test_checkout_recovery_status_is_private():
 r=TestClient(app).get("/api/v1/admin/ithute-pay/orders/00000000-0000-0000-0000-000000000001/attempt")
 assert r.status_code==401
