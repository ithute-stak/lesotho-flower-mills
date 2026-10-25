from fastapi.testclient import TestClient
from app.main import app
def test_alert_list_requires_staff():
 assert TestClient(app).get("/api/v1/admin/reconciliation/alerts").status_code==401
