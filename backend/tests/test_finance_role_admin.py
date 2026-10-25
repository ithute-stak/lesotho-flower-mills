from fastapi.testclient import TestClient
from app.main import app

def test_finance_role_admin_requires_login():
 client=TestClient(app)
 assert client.post("/api/v1/admin/finance-roles/requests",
 json={"identity_subject":"user123","role":"finance_viewer"}).status_code==401
 assert client.get("/api/v1/admin/finance-roles/grants").status_code==401
