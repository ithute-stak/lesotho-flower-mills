from datetime import datetime,timedelta,timezone
from decimal import Decimal
import pytest
from app.promotions_engine import Promotion,quote_promotion

NOW=datetime(2026,10,27,tzinfo=timezone.utc)

def campaign(**changes):
 args=dict(code="BULK",discount_bps=500,starts_at=NOW-timedelta(days=1),
  ends_at=NOW+timedelta(days=1),minimum_subtotal=Decimal("100"),
  maximum_discount=Decimal("20"),audience="business",approved=True)
 args.update(changes)
 return Promotion(**args)

def quote(p,subtotal="200",audience="business"):
 return quote_promotion(p,subtotal=Decimal(subtotal),customer_audience=audience,at=NOW)

def test_approved_discount_is_capped_and_preview_only():
 result=quote(campaign(discount_bps=2000))
 assert result["discount"]==Decimal("20.00")
 assert result["net_subtotal"]==Decimal("180.00")
 assert result["eligible"]
 assert not result["approved_order_total"]
 assert not result["redeemed"]

@pytest.mark.parametrize("promotion,subtotal,audience,reason",[
 (campaign(approved=False),"200","business","not_approved"),
 (campaign(starts_at=NOW+timedelta(minutes=1)),"200","business","outside_campaign_window"),
 (campaign(),"200","public","not_eligible"),
 (campaign(),"99","business","below_minimum_subtotal"),
])
def test_reject_ineligible_campaigns(promotion,subtotal,audience,reason):
 result=quote(promotion,subtotal,audience)
 assert result["reason"]==reason
 assert result["discount"]==0

@pytest.mark.parametrize("change",[
 {"discount_bps":10001},
 {"discount_bps":True},
 {"minimum_subtotal":Decimal("-1")},
 {"maximum_discount":Decimal("NaN")},
 {"starts_at":NOW+timedelta(days=2)},
 {"approved":"true"},
 {"audience":"administrator"},
 {"ends_at":NOW.replace(tzinfo=None)},
])
def test_invalid_campaigns_rejected(change):
 with pytest.raises(ValueError):
  quote(campaign(**change))

def test_rounding_is_deterministic():
 result=quote(campaign(discount_bps=333,maximum_discount=None,minimum_subtotal=Decimal("0")),"100.00")
 assert result["discount"]==Decimal("3.33")
