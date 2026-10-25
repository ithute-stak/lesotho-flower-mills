from fastapi.testclient import TestClient
from app.main import app
from app.security import create_token


def test_publication_requires_login():
    c=TestClient(app)
    assert c.post("/api/v1/admin/price-books/00000000-0000-0000-0000-000000000001/approve").status_code==401
    assert c.post("/api/v1/admin/price-books/00000000-0000-0000-0000-000000000001/publish").status_code==401


def test_publication_rejects_customer_without_db(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET","local-test-secret-not-for-production-123456")
    token=create_token("customer-id","customer")
    r=TestClient(app).post("/api/v1/admin/price-books/00000000-0000-0000-0000-000000000001/publish",headers={"Authorization":"Bearer "+token})
    assert r.status_code==403
