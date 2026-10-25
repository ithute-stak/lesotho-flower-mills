from fastapi.testclient import TestClient
from app.main import app

def test_payment_post_requires_auth():
    r=TestClient(app).post("/api/v1/admin/finance/payments",json={
      "order_id":"00000000-0000-0000-0000-000000000001",
      "provider":"example","provider_reference":"TXN-12345","amount":"3500.00"})
    assert r.status_code==401

def test_confirmation_requires_auth():
    r=TestClient(app).post("/api/v1/admin/finance/orders/00000000-0000-0000-0000-000000000001/confirm-payment")
    assert r.status_code==401

def test_invalid_payment_amount_is_rejected_by_schema():
    from pydantic import ValidationError
    from uuid import UUID
    import pytest
    from app.payment_authorisation import PaymentRecord
    with pytest.raises(ValidationError):
        PaymentRecord(order_id=UUID(int=1),provider="example",
          provider_reference="TXN-12345",amount="0.00")
