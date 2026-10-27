from uuid import UUID
import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import CancelRepeatOrder,cancel_repeat_order,router
from app.finance_permissions import finance_read,finance_review

ID=UUID("00000000-0000-0000-0000-000000000011")

class Result:
 def __init__(self,row):self.row=row
 def first(self):return self.row

class DB:
 def __init__(self,row):self.row=row;self.commits=0;self.rollbacks=0;self.queries=[]
 def execute(self,statement,params):
  self.queries.append((str(statement),params))
  return Result(self.row)
 def commit(self):self.commits+=1
 def rollback(self):self.rollbacks+=1

def test_cancel_draft_only_and_actor_audit():
 db=DB((ID,))
 result=cancel_repeat_order(ID,CancelRepeatOrder(reason="Customer requested cancellation"),{"sub":"reviewer-2"},db)
 assert result["status"]=="cancelled"
 assert result["automatic_ordering_enabled"] is False
 assert db.commits==1
 sql,params=db.queries[0]
 assert "status='draft'" in sql and "RETURNING id" in sql
 assert params["actor"]=="reviewer-2"
 assert params["reason"]=="Customer requested cancellation"

def test_cancel_does_not_modify_non_draft():
 db=DB(None)
 with pytest.raises(HTTPException) as exc:
  cancel_repeat_order(ID,CancelRepeatOrder(reason="Customer requested cancellation"),{"sub":"reviewer-2"},db)
 assert exc.value.status_code==409
 assert db.commits==0 and db.rollbacks==1

def test_cancel_reason_is_required():
 from pydantic import ValidationError
 with pytest.raises(ValidationError):
  CancelRepeatOrder(reason="")

def test_repeat_order_routes_keep_finance_guard():
 for route in router.routes:
  if "/repeat-orders" not in route.path:continue
  permission=finance_read if "GET" in route.methods else finance_review
  assert any(d.call is permission for d in route.dependant.dependencies)
 assert not any("/execute" in route.path or "/activate" in route.path for route in router.routes)
