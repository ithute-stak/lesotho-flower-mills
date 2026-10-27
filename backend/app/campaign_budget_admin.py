"""Finance-controlled campaign budget planning; no checkout spend authority."""
from decimal import Decimal
from uuid import UUID,uuid4
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review,finance_admin

router=APIRouter(prefix="/api/v1/admin/campaign-budgets",tags=["campaign-budgets"])
class BudgetDraft(BaseModel):
 campaign_id:UUID
 limit_amount:Decimal=Field(gt=0,max_digits=18,decimal_places=2)

@router.post("",status_code=201)
def create_budget(body:BudgetDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 campaign=db.execute(text("SELECT status FROM marketing.campaigns WHERE id=:id FOR UPDATE"),
  {"id":body.campaign_id}).mappings().first()
 if not campaign:raise HTTPException(404,"Campaign not found")
 if campaign["status"]=="disabled":raise HTTPException(409,"Campaign disabled")
 bid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.campaign_budgets (id,campaign_id,limit_amount,created_by)
  VALUES (:id,:campaign,:limit,:actor)"""),
  {"id":bid,"campaign":body.campaign_id,"limit":body.limit_amount,"actor":identity["sub"]})
  db.execute(text("""INSERT INTO marketing.campaign_budget_events (id,budget_id,actor_subject,action)
  VALUES (:id,:budget,:actor,'created')"""),{"id":uuid4(),"budget":bid,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"A budget already exists for this campaign")
 return {"id":str(bid),"status":"draft","spending_enabled":False}

@router.post("/{budget_id}/approve")
def approve_budget(budget_id:UUID,identity:dict=Depends(finance_admin),db:Session=Depends(db_session)):
 row=db.execute(text("""SELECT status,created_by FROM marketing.campaign_budgets
 WHERE id=:id FOR UPDATE"""),{"id":budget_id}).mappings().first()
 if not row:raise HTTPException(404,"Budget not found")
 if row["status"]!="draft":raise HTTPException(409,"Only draft budgets can be approved")
 if row["created_by"]==identity["sub"]:raise HTTPException(403,"Budget creator cannot approve")
 db.execute(text("""UPDATE marketing.campaign_budgets SET status='approved',approved_by=:actor WHERE id=:id"""),
  {"id":budget_id,"actor":identity["sub"]})
 db.execute(text("""INSERT INTO marketing.campaign_budget_events (id,budget_id,actor_subject,action)
 VALUES (:id,:budget,:actor,'approved')"""),{"id":uuid4(),"budget":budget_id,"actor":identity["sub"]})
 db.commit()
 return {"id":str(budget_id),"status":"approved","spending_enabled":False}

@router.get("")
def list_budgets(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,campaign_id,limit_amount,currency,status,created_by,approved_by,created_at
 FROM marketing.campaign_budgets ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]
