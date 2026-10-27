import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import ReferralDraft,create_referral_draft,router
from app.finance_permissions import finance_read,finance_review
ID1="00000000-0000-0000-0000-000000000001"
ID2="00000000-0000-0000-0000-000000000002"
class DB:
 def execute(self,*args,**kwargs):raise AssertionError("Should not write self-referral")
def test_no_self_referral():
 with pytest.raises(HTTPException) as e:
  create_referral_draft(ReferralDraft(referrer_customer_id=ID1,referred_customer_id=ID1),{"sub":"reviewer"},DB())
 assert e.value.status_code==422
def test_referral_permissions_and_no_reward_route():
 for route in router.routes:
  if "/referrals" in route.path:
   required=finance_read if "GET" in route.methods else finance_review
   assert any(d.call is required for d in route.dependant.dependencies)
 assert not any("reward" in route.path for route in router.routes)
