"""Regression checks for malformed password hashes and valid credential handling."""
from app.security import hash_password, verify_password


def test_malformed_argon2_hash_is_rejected_without_server_error():
    assert verify_password("not-a-valid-argon2-hash", "any password") is False


def test_valid_argon2_hash_still_verifies():
    password = "synthetic-test-password-123"
    encoded = hash_password(password)
    assert verify_password(encoded, password) is True
    assert verify_password(encoded, "wrong-password") is False


def test_missing_role_claim_is_rejected(monkeypatch):
    from datetime import datetime, timedelta, timezone
    import jwt
    import pytest
    from fastapi import HTTPException
    from app.security import current_identity

    secret = "synthetic-test-secret-which-is-long-enough"
    monkeypatch.setenv("AUTH_SECRET", secret)
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": "synthetic-user", "iat": now, "exp": now + timedelta(minutes=5)},
        secret,
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as error:
        current_identity("Bearer " + token)
    assert error.value.status_code == 401


def test_valid_signed_token_remains_accepted(monkeypatch):
    from app.security import create_token, current_identity

    monkeypatch.setenv("AUTH_SECRET", "synthetic-test-secret-which-is-long-enough")
    token = create_token("synthetic-user", "admin")
    identity = current_identity("Bearer " + token)
    assert identity["sub"] == "synthetic-user"
    assert identity["role"] == "admin"
