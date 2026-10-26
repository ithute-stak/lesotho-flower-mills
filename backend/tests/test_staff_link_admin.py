from fastapi.testclient import TestClient
from app.main import app

def test_link_admin_requires_authentication():
 c=TestClient(app)
 assert c.post("/api/v1/admin/central-staff-links/requests",json={
  "issuer":"https://auth.example.invalid","central_subject":"test-central",
  "local_user_id":"00000000-0000-0000-0000-000000000001"}).status_code==401
 assert c.get("/api/v1/admin/central-staff-links/00000000-0000-0000-0000-000000000001/history").status_code==401
