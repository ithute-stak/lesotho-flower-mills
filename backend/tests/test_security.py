from fastapi.testclient import TestClient
from app.main import app
from app.security import hash_password, verify_password, create_token
import pytest


def test_password_hashing():
    hashed = hash_password("Strong-password-12345")
    assert verify_password(hashed, "Strong-password-12345")
    assert not verify_password(hashed, "wrong")


def test_short_password_rejected():
    with pytest.raises(ValueError):
        hash_password("short")


def test_signed_token(monkeypatch):
    monkeypatch.setenv("AUTH_SECRET", "local-test-secret-not-for-production-123456")
    token = create_token("user-1", "customer")
    with TestClient(app) as client:
        response = client.get("/api/v1/account/me", headers={"Authorization": "Bearer " + token})
    assert response.status_code == 200
    assert response.json()["role"] == "customer"


def test_no_auth_denied():
    response = TestClient(app).post("/api/v1/admin/products", json={"sku": "X123", "name": "Demo"})
    assert response.status_code == 401
