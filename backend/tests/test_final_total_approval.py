from fastapi.testclient import TestClient
from app.main import app
def test_final_approval_authentication():
 c=TestClient(app)
 assert c.post("/api/v1/admin/final-total-approval/00000000-0000-0000-0000-000000000001/approve").status_code==401
 assert c.get("/api/v1/admin/final-total-approval/00000000-0000-0000-0000-000000000001/audit").status_code==401
