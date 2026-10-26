from fastapi.testclient import TestClient
from app.main import app

def test_cancellation_requires_authentication():
 response=TestClient(app).post("/api/v1/admin/orders/00000000-0000-0000-0000-000000000001/cancel")
 assert response.status_code==401
