from app.ithute_auth_readiness import assess_auth_readiness

def test_absent_auth_configuration_fails_closed():
    state=assess_auth_readiness({})
    assert not state["ready"]
    assert "missing_issuer" in state["blockers"]
    assert "central_session_revocation_contract_unverified" in state["blockers"]

def test_supplied_urls_do_not_prove_operational_readiness():
    state=assess_auth_readiness({
        "LFM_ITHUTE_AUTH_ISSUER":"https://auth.example.invalid",
        "LFM_ITHUTE_AUTH_AUDIENCE":"lfm-api",
        "LFM_ITHUTE_AUTH_JWKS_URL":"https://auth.example.invalid/keys",
    })
    assert state["ready"] is False
    assert state["central_auth_enabled"] is False

def test_plaintext_jwks_rejected():
    state=assess_auth_readiness({
        "LFM_ITHUTE_AUTH_ISSUER":"https://auth.example.invalid",
        "LFM_ITHUTE_AUTH_AUDIENCE":"lfm-api",
        "LFM_ITHUTE_AUTH_JWKS_URL":"http://auth.example.invalid/keys",
    })
    assert "invalid_jwks_url" in state["blockers"]
