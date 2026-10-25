import pytest
import jwt
from fastapi import HTTPException
from app.ithute_identity_validation import verify_external_identity

def test_missing_config_is_unavailable(monkeypatch):
    monkeypatch.delenv("LFM_ITHUTE_AUTH_ISSUER",raising=False)
    monkeypatch.delenv("LFM_ITHUTE_AUTH_AUDIENCE",raising=False)
    monkeypatch.delenv("LFM_ITHUTE_AUTH_JWKS_URL",raising=False)
    with pytest.raises(HTTPException) as err:
        verify_external_identity("invalid")
    assert err.value.status_code==503

def test_symmetric_token_rejected(monkeypatch):
    monkeypatch.setenv("LFM_ITHUTE_AUTH_ISSUER","https://auth.example.invalid")
    monkeypatch.setenv("LFM_ITHUTE_AUTH_AUDIENCE","lfm-api")
    monkeypatch.setenv("LFM_ITHUTE_AUTH_JWKS_URL","https://auth.example.invalid/jwks")
    token=jwt.encode({"sub":"user","iss":"https://auth.example.invalid",
                      "aud":"lfm-api","iat":1,"exp":9999999999},
                      "test-key",algorithm="HS256",headers={"kid":"one"})
    with pytest.raises(HTTPException) as err:
        verify_external_identity(token)
    assert err.value.status_code==401
