from fastapi.testclient import TestClient
from app.main import app

def test_grant_event_history_requires_auth():
 assert TestClient(app).get("/api/v1/admin/finance-roles/events").status_code==401
