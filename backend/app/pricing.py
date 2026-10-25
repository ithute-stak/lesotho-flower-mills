"""Deterministic, currency-safe quantity pricing.

Rates are examples only and are not seeded as official LFM prices.
"""
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class Method(str, Enum):
    BUNDLE = "fixed_bundle"
    VOLUME = "volume_all_units"


class Tier(BaseModel):
    minimum_quantity: int = Field(ge=1)
    unit_price: Decimal | None = Field(default=None, ge=0)
    bundle_price: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def check_price(self):
        if (self.unit_price is None) == (self.bundle_price is None):
            raise ValueError("exactly one of unit_price or bundle_price is required")
        return self


class PricingRequest(BaseModel):
    quantity: int = Field(ge=1, le=1000000)
    method: Method
    tiers: list[Tier] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_tiers(self):
        mins = [tier.minimum_quantity for tier in self.tiers]
        if len(mins) != len(set(mins)) or 1 not in mins:
            raise ValueError("tiers must include quantity 1 and have unique breakpoints")
        if self.method == Method.VOLUME and any(t.unit_price is None for t in self.tiers):
            raise ValueError("volume pricing requires unit prices")
        if self.method == Method.BUNDLE and any(t.bundle_price is None for t in self.tiers):
            raise ValueError("bundle pricing requires bundle prices")
        return self


class PricingResult(BaseModel):
    quantity: int
    method: Method
    subtotal: Decimal
    currency: str = "LSL"


def price_order(req: PricingRequest) -> PricingResult:
    tiers = sorted(req.tiers, key=lambda tier: tier.minimum_quantity, reverse=True)
    remaining = req.quantity
    if req.method == Method.VOLUME:
        tier = next(t for t in tiers if req.quantity >= t.minimum_quantity)
        subtotal = tier.unit_price * req.quantity
    else:
        subtotal = Decimal("0")
        for tier in tiers:
            bundle_count, remaining = divmod(remaining, tier.minimum_quantity)
            subtotal += bundle_count * tier.bundle_price
    subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return PricingResult(quantity=req.quantity, method=req.method, subtotal=subtotal)
