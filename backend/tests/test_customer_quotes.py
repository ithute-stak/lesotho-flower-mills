from fastapi.testclient import TestClient
from app.main import app
from app.security import create_token

def test_customer_quote_auth_required():
    c=TestClient(app)
    assert c.post("/api/v1/my/quotations",json={"items":[]}).status_code in (401,422)
    assert c.get("/api/v1/my/quotations").status_code==401

def test_assignment_requires_staff(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET","local-test-secret-not-for-production-123456")
    token=create_token("customer-1","customer")
    r=TestClient(app).post("/api/v1/admin/customer-price-books",headers={"Authorization":"Bearer "+token},
        json={"customer_id":"00000000-0000-0000-0000-000000000001",
              "price_book_id":"00000000-0000-0000-0000-000000000002"})
    assert r.status_code==403
