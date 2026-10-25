from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.main import app
from app.pricing import PricingRequest, price_order

BUNDLES = [
    {"minimum_quantity": 1, "bundle_price": "430.00"},
    {"minimum_quantity": 5, "bundle_price": "2000.00"},
    {"minimum_quantity": 10, "bundle_price": "3500.00"},
]


@pytest.mark.parametrize("quantity,expected", [
    (1, "430.00"), (5, "2000.00"), (10, "3500.00"),
    (7, "2860.00"), (15, "5500.00"), (16, "5930.00"),
])
def test_fixed_bundles(quantity, expected):
    request = PricingRequest(quantity=quantity, method="fixed_bundle", tiers=BUNDLES)
    assert price_order(request).subtotal == Decimal(expected)


def test_volume_all_units():
    req = PricingRequest(quantity=10, method="volume_all_units", tiers=[
        {"minimum_quantity": 1, "unit_price": "430.00"},
        {"minimum_quantity": 5, "unit_price": "400.00"},
        {"minimum_quantity": 10, "unit_price": "350.00"},
    ])
    assert price_order(req).subtotal == Decimal("3500.00")


def test_invalid_price_rules():
    with pytest.raises(ValidationError):
        PricingRequest(quantity=2, method="fixed_bundle", tiers=[{"minimum_quantity": 5, "bundle_price": "50"}])


def test_preview_api():
    response = TestClient(app).post("/api/v1/pricing/preview", json={
        "quantity": 10, "method": "fixed_bundle", "tiers": BUNDLES
    })
    assert response.status_code == 200
    assert Decimal(response.json()["subtotal"]) == Decimal("3500.00")


def test_categories():
    response = TestClient(app).get("/api/v1/categories")
    assert response.status_code == 200
    assert {entry["slug"] for entry in response.json()} == {"feed", "maize", "flour", "sugar"}
