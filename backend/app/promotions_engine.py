"""Deterministic draft-only promotion calculations.

This engine never approves a campaign, reserves stock, redeems a coupon,
changes an order, or authorises a payable total.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

@dataclass(frozen=True)
class Promotion:
    code: str
    discount_bps: int
    starts_at: datetime
    ends_at: datetime
    minimum_subtotal: Decimal = Decimal("0")
    maximum_discount: Decimal | None = None
    audience: str = "public"
    approved: bool = False

def quote_promotion(promotion: Promotion, *, subtotal: Decimal,
                    customer_audience: str, at: datetime | None = None) -> dict:
    """Preview at most one promotion, with explicit rejection reasons.

    Call only with a server-approved promotion record; the approved field must
    never originate from a client request.
    """
    now = at or datetime.now(timezone.utc)
    if any(d.tzinfo is None or d.utcoffset() is None
           for d in (now, promotion.starts_at, promotion.ends_at)):
        raise ValueError("Timezone-aware times required")
    if not isinstance(promotion.approved, bool):
        raise ValueError("Approval must be boolean")
    if not isinstance(promotion.discount_bps, int) or isinstance(promotion.discount_bps, bool):
        raise ValueError("Invalid discount basis points")
    if not 0 <= promotion.discount_bps <= 10000:
        raise ValueError("Discount outside permitted range")
    amounts = (subtotal, promotion.minimum_subtotal)
    if promotion.maximum_discount is not None:
        amounts += (promotion.maximum_discount,)
    if any(not amount.is_finite() or amount < 0 for amount in amounts):
        raise ValueError("Invalid promotion amounts")
    if promotion.ends_at <= promotion.starts_at:
        raise ValueError("Invalid promotion period")
    if promotion.audience not in ("public", "business"):
        raise ValueError("Invalid promotion audience")
    if customer_audience not in ("public", "business"):
        raise ValueError("Invalid customer audience")
    reason = None
    if not promotion.approved:
        reason = "not_approved"
    elif not promotion.starts_at <= now < promotion.ends_at:
        reason = "outside_campaign_window"
    elif promotion.audience != customer_audience:
        reason = "not_eligible"
    elif subtotal < promotion.minimum_subtotal:
        reason = "below_minimum_subtotal"
    discount = Decimal("0.00")
    if reason is None:
        discount = (subtotal * Decimal(promotion.discount_bps) / Decimal(10000)).quantize(CENT, rounding=ROUND_HALF_UP)
        if promotion.maximum_discount is not None:
            discount = min(discount, promotion.maximum_discount.quantize(CENT, rounding=ROUND_HALF_UP))
        discount = min(discount, subtotal)
    return {"eligible": reason is None, "reason": reason,
            "discount": discount, "net_subtotal": subtotal - discount,
            "approved_order_total": False, "redeemed": False}
