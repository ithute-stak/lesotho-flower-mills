from app.ithute_auth_contract import preflight

def test_preflight_needs_explicit_config():
    result=preflight({})
    assert not result.ready_for_registration
    assert "LFM_ITHUTE_AUTH_CLIENT_ID" in result.missing

def test_preflight_rejects_insecure_callback():
    result=preflight({
      "LFM_ITHUTE_AUTH_ISSUER":"https://auth.ithute.co.ls",
      "LFM_ITHUTE_AUTH_CLIENT_ID":"lesotho-flour-mills-customer",
      "LFM_ITHUTE_AUTH_CALLBACK_URL":"http://lfm.example.org/callback",
      "LFM_ITHUTE_AUTH_SESSION_SECRET":"a"*40,
    })
    assert not result.ready_for_registration
    assert "valid_https_callback" in result.missing

def test_preflight_valid_fields_are_only_registration_readiness():
    result=preflight({
      "LFM_ITHUTE_AUTH_ISSUER":"https://auth.ithute.co.ls",
      "LFM_ITHUTE_AUTH_CLIENT_ID":"lesotho-flour-mills-customer",
      "LFM_ITHUTE_AUTH_CALLBACK_URL":"https://lfm.example.org/api/auth/ithute/callback",
      "LFM_ITHUTE_AUTH_SESSION_SECRET":"a"*40,
    })
    assert result.ready_for_registration
