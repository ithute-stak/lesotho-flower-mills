from decimal import Decimal
import httpx
import pytest
from app.ithute_pay_adapter import CheckoutRequest,IthutePayCheckoutAdapter


def test_payload_uses_server_amount():
    request=CheckoutRequest("LFM-ORD-123",Decimal("2000.00"))
    assert request.payload()["amount"]=="2000.00"
    with pytest.raises(ValueError):
        CheckoutRequest("X",Decimal("-5")).payload()


def test_checkout_contract_request_headers():
    recorded=[]
    def mock(req):
        recorded.append(req)
        return httpx.Response(201,json={"public_id":"cs_123","checkout_url":"https://pay.ithute.co.ls/pay/test",
            "status":"created","reference":"LFM-ORD-123","amount":"2000.00","currency":"LSL"})
    with httpx.Client(transport=httpx.MockTransport(mock)) as client:
        adapter=IthutePayCheckoutAdapter("https://api.pay.ithute.co.ls/api/v1","ipb_test_dummy",client)
        response=adapter.create_checkout(CheckoutRequest("LFM-ORD-123",Decimal("2000.00")),idempotency_key="lfm-order-123")
    assert response["status"]=="created"
    assert recorded[0].headers["Idempotency-Key"]=="lfm-order-123"
    assert recorded[0].headers["Authorization"]=="Bearer ipb_test_dummy"
    assert recorded[0].url.path=="/api/v1/checkout-sessions"


def test_mismatched_amount_fails_closed():
    def mock(req):
        return httpx.Response(201,json={"public_id":"cs_123","checkout_url":"https://pay.ithute.co.ls/pay/test",
          "status":"created","reference":"LFM-ORD-123","amount":"1.00","currency":"LSL"})
    with httpx.Client(transport=httpx.MockTransport(mock)) as client:
        adapter=IthutePayCheckoutAdapter("https://api.pay.ithute.co.ls/api/v1","ipb_test_dummy",client)
        with pytest.raises(ValueError):
            adapter.create_checkout(CheckoutRequest("LFM-ORD-123",Decimal("2000.00")),idempotency_key="unique-123")
