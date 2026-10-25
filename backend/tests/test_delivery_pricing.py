from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.delivery_pricing import transport_fee

def test_flat_tariff():
 assert transport_fee(Decimal("430"),Decimal("75"))==Decimal("75.00")
def test_free_delivery_threshold():
 assert transport_fee(Decimal("2000"),Decimal("75"),Decimal("2000"))==Decimal("0.00")
def test_invalid_tariff_fails_closed():
 with pytest.raises(ValueError):transport_fee(Decimal("100"),Decimal("-1"))
def test_requires_authentication():
 r=TestClient(app).post("/api/v1/admin/delivery-pricing/preview",json={
 "order_id":"00000000-0000-0000-0000-000000000001","fulfilment_method":"collection"})
 assert r.status_code==401
