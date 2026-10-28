"""Regression checks for malformed password hashes and valid credential handling."""
from app.security import hash_password, verify_password


def test_malformed_argon2_hash_is_rejected_without_server_error():
    assert verify_password("not-a-valid-argon2-hash", "any password") is False


def test_valid_argon2_hash_still_verifies():
    password = "synthetic-test-password-123"
    encoded = hash_password(password)
    assert verify_password(encoded, password) is True
    assert verify_password(encoded, "wrong-password") is False
