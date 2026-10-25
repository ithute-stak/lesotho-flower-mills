"""Server-only Ithute Pay checkout adapter (not yet wired to live orders).

Contract inspected from ithute-pay/apps/backend/routers/checkout.py and
database/schemas/checkout.py. Never accept amounts from a browser.
"""
from dataclasses import dataclass
from decimal import Decimal
from urllib.parse import urlsplit
import httpx


@dataclass(frozen=True)
class CheckoutRequest:
    order_number: str
    amount: Decimal
    currency: str = "LSL"

    def payload(self) -> dict:
        if self.amount <= 0 or self.currency != "LSL":
            raise ValueError("A positive LSL amount is required")
        if not self.order_number or len(self.order_number) > 100:
            raise ValueError("Invalid sales order reference")
        return {"amount": str(self.amount), "currency": self.currency,
                "reference": self.order_number,
                "description": "Lesotho Flour Mills order " + self.order_number,
                "expires_in_minutes": 60}


class IthutePayCheckoutAdapter:
    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        parsed = urlsplit(base_url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("IthutePay must use a trusted HTTPS endpoint")
        if not (api_key.startswith("ipb_test_") or api_key.startswith("ipb_live_")):
            raise ValueError("Invalid application credential prefix")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = client

    def create_checkout(self, request: CheckoutRequest, *, idempotency_key: str) -> dict:
        if not idempotency_key or len(idempotency_key)>128:
            raise ValueError("A unique idempotency key is required")
        response = self.client.post(
            self.base_url + "/checkout-sessions",
            json=request.payload(),
            headers={"Authorization": "Bearer " + self.api_key,
                     "Idempotency-Key": idempotency_key,
                     "Accept": "application/json"},
            timeout=15.0)
        response.raise_for_status()
        result = response.json()
        if result.get("reference") != request.order_number or result.get("currency") != request.currency:
            raise ValueError("Payment provider response does not match the order")
        if Decimal(str(result["amount"])) != request.amount:
            raise ValueError("Payment provider returned an amount mismatch")
        return {"payment_session_id": result["public_id"],
                "checkout_url": result["checkout_url"],
                "status": result["status"]}

    def get_checkout(self, session_id: str) -> dict:
        if not session_id.startswith("cs_") or not session_id.replace("_","").isalnum():
            raise ValueError("Invalid checkout session identifier")
        response = self.client.get(self.base_url + "/checkout-sessions/" + session_id,
            headers={"Authorization": "Bearer " + self.api_key,"Accept":"application/json"},
            timeout=15.0)
        response.raise_for_status()
        return response.json()
