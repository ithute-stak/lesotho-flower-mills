from datetime import datetime,timezone,timedelta
import pytest
from pydantic import ValidationError
from fastapi import HTTPException
from app.campaign_admin import CampaignDraft,approve_campaign,create_campaign,router
from app.finance_permissions import finance_read,finance_review,finance_admin

NOW=datetime(2026,10,27,tzinfo=timezone.utc)

def test_requires_timezone_aware_ordered_campaign_window():
 with pytest.raises(ValidationError):
  CampaignDraft(code="TEST",discount_bps=500,audience="public",
   starts_at=NOW.replace(tzinfo=None),ends_at=NOW+timedelta(days=1))
 with pytest.raises(ValidationError):
  CampaignDraft(code="TEST",discount_bps=500,audience="public",
   starts_at=NOW,ends_at=NOW)

def test_finance_dependencies_bound_to_campaign_operations():
 paths={(route.path,method):route for route in router.routes for method in getattr(route,"methods",[])}
 cases=[
  ("/api/v1/admin/campaigns","POST",finance_review),
  ("/api/v1/admin/campaigns","GET",finance_read),
  ("/api/v1/admin/campaigns/{campaign_id}/approve","POST",finance_admin)]
 for path,method,required in cases:
  route=paths[(path,method)]
  assert any(dep.call is required for dep in route.dependant.dependencies)
 assert not any("/api/v1/public/" in path for path,_ in paths)

class _Result:
 def __init__(self,row):self.row=row
 def mappings(self):return self
 def first(self):return self.row
class _DB:
 def __init__(self,row):self.row=row;self.commits=0
 def execute(self,*args,**kwargs):return _Result(self.row)
 def commit(self):self.commits+=1

def test_creator_cannot_approve_own_draft():
 with pytest.raises(HTTPException) as error:
  approve_campaign("00000000-0000-0000-0000-000000000001",
   {"sub":"maker"},_DB({"status":"draft","created_by":"maker"}))
 assert error.value.status_code==403

def test_non_draft_cannot_be_approved():
 with pytest.raises(HTTPException) as error:
  approve_campaign("00000000-0000-0000-0000-000000000001",
   {"sub":"reviewer"},_DB({"status":"approved","created_by":"maker"}))
 assert error.value.status_code==409
