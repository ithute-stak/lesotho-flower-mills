from fastapi.testclient import TestClient
from app.main import app

def test_delivery_history_requires_authentication():
 assert TestClient(app).get("/api/v1/admin/reconciliation/email-deliveries").status_code==401
