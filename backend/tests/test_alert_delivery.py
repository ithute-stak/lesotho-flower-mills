from app.alert_delivery import configured,deliver_one
def test_delivery_disabled_by_default(monkeypatch):
 monkeypatch.delenv("LFM_FINANCE_EMAIL_DELIVERY_ENABLED",raising=False)
 assert not configured()
 assert deliver_one(None)=={"enabled":False,"reason":"delivery_disabled"}
def test_delivery_explicit_opt_in(monkeypatch):
 monkeypatch.setenv("LFM_FINANCE_EMAIL_DELIVERY_ENABLED","true")
 assert configured()
