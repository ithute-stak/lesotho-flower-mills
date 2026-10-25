from decimal import Decimal
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.payment_gateway import SandboxProvider

def test_sandbox_never_confirms_payment():
    intent=SandboxProvider().initiate(Decimal("430.00"),"LSL",UUID(int=1))
    assert intent.state=="pending"
    assert intent.redirect_url is None
    assert intent.provider_reference.startswith("sandbox-")

def test_gateway_requires_auth():
    c=TestClient(app)
    assert c.get("/api/v1/admin/payment-gateway/providers").status_code==401
    assert c.post("/api/v1/admin/payment-gateway/initiate",
      json={"order_id":"00000000-0000-0000-0000-000000000001","provider":"sandbox"}).status_code==401
