from fastapi.testclient import TestClient
from app.main import app
def test_driver_endpoints_require_login():
 c=TestClient(app)
 assert c.get("/api/v1/driver/assignments").status_code==401
 assert c.get("/api/v1/driver/assignments/00000000-0000-0000-0000-000000000001").status_code==401
