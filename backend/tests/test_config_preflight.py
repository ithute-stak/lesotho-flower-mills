from app.config_preflight import configuration_issues,assert_safe_production_configuration
import pytest

SAFE={"LFM_ENV":"production","AUTH_SECRET":"secure-random-ci-value-0123456789-abcdef",
"DATABASE_URL":"postgresql+psycopg://service:synthetic-pass@db.internal:5432/lfm",
"LFM_SANDBOX_PAYMENTS_ENABLED":"false","LFM_ITHUTE_PAY_CHECKOUT_ENABLED":"false"}
def test_safe_production_baseline():
 assert configuration_issues(SAFE)==[]
 assert assert_safe_production_configuration(SAFE) is None

@pytest.mark.parametrize("override",[
 {"AUTH_SECRET":"replace-with-a-secure-random-secret-at-least-32-characters"},
 {"AUTH_SECRET":"short"},
 {"DATABASE_URL":"sqlite:///test.db"},
 {"LFM_SANDBOX_PAYMENTS_ENABLED":"true"},
 {"LFM_ITHUTE_PAY_CHECKOUT_ENABLED":"true"},
 {"LFM_E2E_SEED":"true"},
])
def test_production_preflight_rejects_unsafe_settings(override):
 e={**SAFE,**override}
 assert configuration_issues(e)
 with pytest.raises(RuntimeError):
  assert_safe_production_configuration(e)
