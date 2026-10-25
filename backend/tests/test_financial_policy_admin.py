from fastapi.testclient import TestClient
from app.main import app
from app.financial_policy_admin import NewPolicy
from pydantic import ValidationError
import pytest
def test_financial_policy_admin_requires_auth():
 client=TestClient(app)
 assert client.get("/api/v1/admin/financial-policies").status_code==401
 assert client.post("/api/v1/admin/financial-policies",json={"code":"STANDARD","version":1,"tax_rate_bps":0}).status_code==401
 assert client.post("/api/v1/admin/financial-policies/00000000-0000-0000-0000-000000000001/approve").status_code==401
def test_invalid_rates_rejected():
 with pytest.raises(ValidationError):NewPolicy(code="standard",version=1,tax_rate_bps=12000)
