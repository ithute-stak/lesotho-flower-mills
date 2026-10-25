from fastapi.testclient import TestClient
from app.main import app
def test_delivery_requires_authentication():
 client=TestClient(app)
 assert client.post("/api/v1/admin/delivery/assignments",json={"order_id":"00000000-0000-0000-0000-000000000001","driver_id":"00000000-0000-0000-0000-000000000002","vehicle_id":"00000000-0000-0000-0000-000000000003"}).status_code==401
 assert client.post("/api/v1/admin/delivery/assignments/00000000-0000-0000-0000-000000000001/dispatch").status_code==401
