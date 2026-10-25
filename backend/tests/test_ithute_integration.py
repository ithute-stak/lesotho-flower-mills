import pytest
from app.ithute_integration import IthuteIntegration,is_https_endpoint


def test_disabled_by_default(monkeypatch):
    for key in ("LFM_ITHUTE_AUTH_ENABLED","LFM_ITHUTE_PAY_ENABLED"):
        monkeypatch.delenv(key,raising=False)
    config=IthuteIntegration.configured()
    assert not config.auth_enabled
    assert not config.pay_enabled


def test_flags_fail_closed_without_adapters(monkeypatch):
    monkeypatch.setenv("LFM_ITHUTE_PAY_ENABLED","true")
    with pytest.raises(RuntimeError):
        IthuteIntegration.configured()


def test_only_https_service_endpoints():
    assert is_https_endpoint("https://api.pay.ithute.co.ls")
    assert not is_https_endpoint("http://api.pay.ithute.co.ls")
    assert not is_https_endpoint("https://user:password@example.com")
