from fastapi.testclient import TestClient
from app.main import app

def test_queue_and_history_require_auth():
 c=TestClient(app)
 assert c.get("/api/v1/admin/reconciliation/queue").status_code==401
 assert c.get("/api/v1/admin/reconciliation/attempts/00000000-0000-0000-0000-000000000001/history").status_code==401
