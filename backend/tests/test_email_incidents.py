from fastapi.testclient import TestClient
from app.main import app
def test_incident_review_endpoints_require_staff():
 c=TestClient(app)
 uid="00000000-0000-0000-0000-000000000001"
 assert c.get("/api/v1/admin/notification-incidents/"+uid+"/reviews").status_code==401
 assert c.post("/api/v1/admin/notification-incidents/"+uid+"/reviews",
 json={"disposition":"investigating","note":"Reviewing SMTP provider logs"}).status_code==401
