from fastapi.testclient import TestClient
from app.main import app
from app.security import create_token


def test_staff_routes_require_auth():
    client=TestClient(app)
    assert client.get("/api/v1/admin/price-books").status_code==401
    assert client.get("/api/v1/admin/businesses/pending").status_code==401
    assert client.post("/api/v1/admin/price-books/book/items",json={"product_id":"x","method":"fixed_bundle","tiers":[{"minimum_quantity":1,"bundle_price":"430"}]}).status_code==401


def test_customer_cannot_manage_prices(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET","local-test-secret-not-for-production-123456")
    token=create_token("customer-id","customer")
    result=TestClient(app).get("/api/v1/admin/price-books",headers={"Authorization":"Bearer "+token})
    assert result.status_code==403
