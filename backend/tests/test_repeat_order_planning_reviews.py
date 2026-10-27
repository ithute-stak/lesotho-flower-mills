from uuid import UUID
import pytest
from fastapi import HTTPException
from app.customer_engagement_admin import PlanningReview,review_repeat_order,router
from app.finance_permissions import finance_read,finance_review
ID=UUID("00000000-0000-0000-0000-000000000011")

class QueryResult:
 def __init__(self,values):self.values=values
 def first(self):return self.values

class FakeDB:
 def __init__(self,found=True):self.found=found;self.statements=[];self.commits=0;self.rollbacks=0
 def execute(self,sql,params):
  self.statements.append((str(sql),params))
  return QueryResult((ID,) if self.found else None)
 def commit(self):self.commits+=1
 def rollback(self):self.rollbacks+=1

def test_independent_review_writes_audit_and_no_orders():
 db=FakeDB()
 result=review_repeat_order(ID,"approve",PlanningReview(note="Approved for planning"),{"sub":"independent-reviewer"},db)
 assert result["status"]=="approved"
 assert result["planning_only"] is True and result["automatic_ordering_enabled"] is False
 assert db.commits==1 and len(db.statements)==2
 assert "created_by<>:actor" in db.statements[0][0]
 assert "status='draft'" in db.statements[0][0]
 assert "repeat_order_review_events" in db.statements[1][0]

def test_already_reviewed_or_self_review_rejected():
 db=FakeDB(found=False)
 with pytest.raises(HTTPException) as exc:
  review_repeat_order(ID,"approve",PlanningReview(note="Not authorised"),{"sub":"same-creator"},db)
 assert exc.value.status_code==409
 assert db.commits==0

def test_rejection_and_invalid_decision():
 db=FakeDB()
 assert review_repeat_order(ID,"reject",PlanningReview(note="Incorrect planned quantity"),{"sub":"reviewer"},db)["status"]=="rejected"
 with pytest.raises(HTTPException) as exc:
  review_repeat_order(ID,"activate",PlanningReview(note="Do not activate"),{"sub":"reviewer"},FakeDB())
 assert exc.value.status_code==422

def test_finance_permissions():
 for route in router.routes:
  if "/repeat-orders/" not in route.path or ("/review/" not in route.path and "/reviews" not in route.path):continue
  required=finance_read if "GET" in route.methods else finance_review
  assert any(dep.call is required for dep in route.dependant.dependencies)
