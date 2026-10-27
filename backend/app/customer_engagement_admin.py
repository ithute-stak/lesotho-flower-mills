"""Internal customer engagement drafts; no loyalty credits or scheduled orders."""
from uuid import UUID,uuid4
from datetime import date
import csv
import io
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from xml.sax.saxutils import escape
from fastapi.responses import Response
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read,finance_review
router=APIRouter(prefix="/api/v1/admin/customer-engagement",tags=["customer-engagement"])

class LoyaltyDraft(BaseModel):
 customer_id:UUID

class RepeatOrderDraft(BaseModel):
 customer_id:UUID
 product_id:UUID
 quantity:int=Field(ge=1,le=1000000)
 frequency:str=Field(pattern="^(weekly|monthly)$")

class CancelRepeatOrder(BaseModel):
 reason:str=Field(min_length=5,max_length=500)

class PlanningReview(BaseModel):
 note:str=Field(min_length=5,max_length=500)

class ReferralDraft(BaseModel):
 referrer_customer_id:UUID
 referred_customer_id:UUID

@router.post("/referrals",status_code=201)
def create_referral_draft(body:ReferralDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 if body.referrer_customer_id==body.referred_customer_id:
  raise HTTPException(422,"Self-referrals are not permitted")
 rid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.referral_plans
  (id,referrer_customer_id,referred_customer_id,created_by)
  VALUES (:id,:referrer,:referred,:actor)"""),
  {"id":rid,"referrer":body.referrer_customer_id,
   "referred":body.referred_customer_id,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Duplicate referral or invalid customer")
 return {"id":str(rid),"status":"draft","rewards_enabled":False}

@router.get("/referrals")
def list_referral_drafts(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,referrer_customer_id,referred_customer_id,status,created_by,created_at
 FROM marketing.referral_plans ORDER BY created_at DESC LIMIT 200""")).mappings().all()
 return [dict(r) for r in rows]

@router.get("/repeat-orders")
def list_repeat_orders(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT id,customer_id,product_id,quantity,frequency,status,created_by,created_at,cancelled_by,cancelled_at,cancellation_reason,reviewed_by,reviewed_at,review_note
 FROM marketing.repeat_order_templates ORDER BY created_at DESC,id DESC LIMIT 200""")).mappings().all()
 return [dict(row) for row in rows]

@router.post("/repeat-orders/{template_id}/cancel")
def cancel_repeat_order(template_id:UUID,body:CancelRepeatOrder,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 if len(body.reason.strip())<5:
  raise HTTPException(422,"Cancellation reason must have at least five non-whitespace characters")
 row=db.execute(text("""UPDATE marketing.repeat_order_templates
 SET status='cancelled',cancelled_by=:actor,cancelled_at=now(),cancellation_reason=:reason
 WHERE id=:id AND status='draft' RETURNING id"""),
 {"id":template_id,"actor":identity["sub"],"reason":body.reason.strip()}).first()
 if row is None:
  db.rollback()
  raise HTTPException(409,"Template is not a draft or does not exist")
 db.commit()
 return {"id":str(template_id),"status":"cancelled","automatic_ordering_enabled":False}

@router.post("/repeat-orders/{template_id}/review/{decision}")
def review_repeat_order(template_id:UUID,decision:str,body:PlanningReview,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 if decision not in ("approve","reject"):
  raise HTTPException(422,"Unsupported review decision")
 if len(body.note.strip())<5:
  raise HTTPException(422,"Review note must contain at least five characters")
 actor=identity["sub"]
 state="approved" if decision=="approve" else "rejected"
 try:
  row=db.execute(text("""UPDATE marketing.repeat_order_templates
  SET status=:state,reviewed_by=:actor,reviewed_at=now(),review_note=:note
  WHERE id=:id AND status='draft' AND created_by<>:actor RETURNING id"""),
  {"id":template_id,"state":state,"actor":actor,"note":body.note.strip()}).first()
  if row is None:
   db.rollback()
   raise HTTPException(409,"Draft not found, already reviewed or self-review prohibited")
  db.execute(text("""INSERT INTO marketing.repeat_order_review_events
   (id,template_id,action,actor,note) VALUES (:event,:id,:state,:actor,:note)"""),
   {"event":uuid4(),"id":template_id,"state":state,"actor":actor,"note":body.note.strip()})
  db.commit()
 except Exception:
  db.rollback()
  raise
 return {"id":str(template_id),"status":state,"planning_only":True,"automatic_ordering_enabled":False}

@router.get("/repeat-orders/{template_id}/reviews")
def repeat_order_reviews(template_id:UUID,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT action,actor,note,created_at FROM marketing.repeat_order_review_events
 WHERE template_id=:id ORDER BY created_at DESC,id DESC LIMIT 100"""),{"id":template_id}).mappings().all()
 return [dict(row) for row in rows]

def _audit_rows(db:Session,status:str|None,actor:str|None,start:date|None,end:date|None,limit:int,offset:int):
 if start and end and start>end:
  raise HTTPException(422,"Start date cannot follow end date")
 if status and status not in ("approved","rejected"):
  raise HTTPException(422,"Unsupported review status")
 return db.execute(text("""SELECT e.id,e.template_id,e.action,e.actor,e.note,e.created_at,
 t.customer_id,t.product_id,t.frequency,t.quantity,t.created_by
 FROM marketing.repeat_order_review_events e
 JOIN marketing.repeat_order_templates t ON t.id=e.template_id
 WHERE (:status IS NULL OR e.action=:status)
 AND (:actor IS NULL OR e.actor=:actor)
 AND (:start IS NULL OR e.created_at >= CAST(:start AS date))
 AND (:end IS NULL OR e.created_at < CAST(:end AS date)+INTERVAL '1 day')
 ORDER BY e.created_at DESC,e.id DESC LIMIT :limit OFFSET :offset"""),
 {"status":status,"actor":actor,"start":start,"end":end,"limit":limit,"offset":offset}).mappings().all()

@router.get("/reports/review-audit")
def engagement_review_audit(status:str|None=None,actor:str|None=None,start:date|None=None,end:date|None=None,
 limit:int=100,offset:int=0,identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 if not 1<=limit<=200 or not 0<=offset<=100000:
  raise HTTPException(422,"Invalid audit pagination")
 return {"basis":"planning_only","items":[dict(r) for r in _audit_rows(db,status,actor,start,end,limit,offset)],
 "limit":limit,"offset":offset}

@router.get("/reports/review-audit.csv")
def engagement_review_audit_csv(status:str|None=None,actor:str|None=None,start:date|None=None,end:date|None=None,
 identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=_audit_rows(db,status,actor,start,end,5000,0)
 output=io.StringIO()
 writer=csv.writer(output)
 fields=["id","template_id","action","actor","note","created_at","customer_id","product_id","frequency","quantity","created_by"]
 writer.writerow(["PLANNING ONLY - not evidence of customer orders or revenue"])
 writer.writerow(fields)
 for row in rows:
  values=[]
  for key in fields:
   value="" if row[key] is None else str(row[key])
   if value.lstrip().startswith(("=","+","-","@")):
    value="'"+value
   values.append(value)
  writer.writerow(values)
 return Response(content=output.getvalue(),media_type="text/csv; charset=utf-8",
 headers={"Content-Disposition":"attachment; filename=customer-engagement-review-audit.csv",
 "Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})

@router.post("/loyalty",status_code=201)
def create_loyalty_draft(body:LoyaltyDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 eid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.loyalty_enrolments (id,customer_id,created_by)
  VALUES (:id,:customer,:actor)"""),{"id":eid,"customer":body.customer_id,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Customer already enrolled in a draft or customer not found")
 return {"id":str(eid),"status":"draft","points_enabled":False}

@router.post("/repeat-orders",status_code=201)
def create_repeat_order_draft(body:RepeatOrderDraft,identity:dict=Depends(finance_review),db:Session=Depends(db_session)):
 tid=uuid4()
 try:
  db.execute(text("""INSERT INTO marketing.repeat_order_templates
  (id,customer_id,product_id,quantity,frequency,created_by)
  VALUES (:id,:customer,:product,:quantity,:frequency,:actor)"""),
  {"id":tid,"customer":body.customer_id,"product":body.product_id,
   "quantity":body.quantity,"frequency":body.frequency,"actor":identity["sub"]})
  db.commit()
 except IntegrityError:
  db.rollback();raise HTTPException(409,"Customer or product not found")
 return {"id":str(tid),"status":"draft","automatic_ordering_enabled":False}

@router.get("/reports/management")
def engagement_management_report(start:date|None=None,end:date|None=None,
 identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 if start and end and start>end:
  raise HTTPException(422,"Start date cannot follow end date")
 params={"start":start,"end":end}
 rows=db.execute(text("""SELECT e.actor,e.action,COUNT(*) AS decisions,
 ROUND(AVG(EXTRACT(EPOCH FROM (e.created_at-t.created_at))/3600)::numeric,2) AS avg_turnaround_hours
 FROM marketing.repeat_order_review_events e
 JOIN marketing.repeat_order_templates t ON t.id=e.template_id
 WHERE (:start IS NULL OR e.created_at>=CAST(:start AS date))
 AND (:end IS NULL OR e.created_at<CAST(:end AS date)+INTERVAL '1 day')
 GROUP BY e.actor,e.action ORDER BY decisions DESC,e.actor,e.action LIMIT 100"""),params).mappings().all()
 trends=db.execute(text("""SELECT TO_CHAR(DATE_TRUNC('month',e.created_at),'YYYY-MM') AS month,
 e.action,COUNT(*) AS decisions
 FROM marketing.repeat_order_review_events e
 WHERE (:start IS NULL OR e.created_at>=CAST(:start AS date))
 AND (:end IS NULL OR e.created_at<CAST(:end AS date)+INTERVAL '1 day')
 GROUP BY DATE_TRUNC('month',e.created_at),e.action
 ORDER BY month DESC,e.action LIMIT 120"""),params).mappings().all()
 totals=db.execute(text("""SELECT COUNT(*) AS total_decisions,
 COUNT(*) FILTER (WHERE action='approved') AS approvals,
 COUNT(*) FILTER (WHERE action='rejected') AS rejections
 FROM marketing.repeat_order_review_events
 WHERE (:start IS NULL OR created_at>=CAST(:start AS date))
 AND (:end IS NULL OR created_at<CAST(:end AS date)+INTERVAL '1 day')"""),params).mappings().one()
 decisions=int(totals["total_decisions"])
 approvals=int(totals["approvals"])
 rejections=int(totals["rejections"])
 return {"basis":"planning_review_only","kpis":{"total_decisions":decisions,"approvals":approvals,"rejections":rejections,"approval_share_percent":round(100*approvals/decisions,1) if decisions else None}, "reviewer_activity":[dict(r) for r in rows],
 "monthly_trends":[dict(r) for r in trends],"actual_sales":None,
 "actual_customer_retention":None,"automatic_ordering_enabled":False}

@router.get("/reports/management.pdf")
def engagement_management_pdf(start:date|None=None,end:date|None=None,
 identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 report=engagement_management_report(start=start,end=end,identity=identity,db=db)
 buffer=io.BytesIO()
 doc=SimpleDocTemplate(buffer,pagesize=(210*mm,297*mm),leftMargin=17*mm,rightMargin=17*mm,topMargin=18*mm,bottomMargin=18*mm)
 styles=getSampleStyleSheet()
 story=[Paragraph("LESOTHO FLOUR MILLS",styles["Title"]),
 Paragraph("Customer Engagement — Planning Review Management Report",styles["Heading2"]),
 Paragraph("INTERNAL PLANNING ONLY • Not evidence of sales, customer retention, payments or fulfilled orders.",styles["Normal"]),
 Paragraph("Reporting period: "+escape(str(start or "All available"))+" to "+escape(str(end or "All available")),styles["Normal"]),Spacer(1,8*mm),
 Paragraph("Planning decisions: "+str(report["kpis"]["total_decisions"])+" | Approved: "+str(report["kpis"]["approvals"])+" | Rejected: "+str(report["kpis"]["rejections"]),styles["Normal"]),
 Paragraph("Approval share: "+(str(report["kpis"]["approval_share_percent"])+"%" if report["kpis"]["approval_share_percent"] is not None else "N/A (no decisions)"),styles["Normal"]),Spacer(1,5*mm),
 Paragraph("Reviewer decisions and average turnaround",styles["Heading3"])]
 activity=[["Reviewer","Decision","Count","Avg hours"]]
 for item in report["reviewer_activity"]:
  activity.append([str(item["actor"])[:42],str(item["action"]),str(item["decisions"]),str(item["avg_turnaround_hours"] if item["avg_turnaround_hours"] is not None else "N/A")])
 if len(activity)==1:activity.append(["No planning reviews in period","","",""])
 t=Table(activity,colWidths=[75*mm,35*mm,22*mm,35*mm],repeatRows=1,hAlign="LEFT")
 t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#15324b")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.3,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
 story.extend([t,Spacer(1,7*mm),Paragraph("Monthly decision trend",styles["Heading3"])])
 trends=[["Month","Decision","Count"]]
 for item in report["monthly_trends"]:trends.append([str(item["month"]),str(item["action"]),str(item["decisions"])])
 if len(trends)==1:trends.append(["No planning reviews in period","",""])
 t2=Table(trends,colWidths=[55*mm,65*mm,47*mm],repeatRows=1,hAlign="LEFT")
 t2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#15324b")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.3,colors.grey),("FONTSIZE",(0,0),(-1,-1),8)]))
 story.extend([t2,Spacer(1,8*mm),Paragraph("Approval decisions are administrative only. Automatic ordering, loyalty rewards, stock reservations and payment effects remain disabled.",styles["Normal"])])
 doc.build(story)
 return Response(content=buffer.getvalue(),media_type="application/pdf",headers={"Content-Disposition":"attachment; filename=customer-engagement-management.pdf","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})

@router.get("/reports/planning")
def engagement_planning_report(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 """Planning-only aggregates. No inference about completed orders or revenue."""
 frequencies=db.execute(text("""SELECT frequency,status,COUNT(*) AS template_count,
 COALESCE(SUM(quantity),0) AS planned_quantity_per_cycle
 FROM marketing.repeat_order_templates
 GROUP BY frequency,status ORDER BY frequency,status""")).mappings().all()
 referrers=db.execute(text("""SELECT referrer_customer_id,COUNT(*) AS referral_count
 FROM marketing.referral_plans GROUP BY referrer_customer_id
 ORDER BY referral_count DESC,referrer_customer_id LIMIT 20""")).mappings().all()
 loyalty=db.execute(text("SELECT COUNT(*) FROM marketing.loyalty_enrolments WHERE status='draft'")).scalar_one()
 referrals=db.execute(text("SELECT COUNT(*) FROM marketing.referral_plans WHERE status='draft'")).scalar_one()
 return {"basis":"planning_only","draft_loyalty_enrolments":loyalty,
 "draft_referrals":referrals,"repeat_order_frequency_breakdown":[dict(r) for r in frequencies],
 "top_referrers":[dict(r) for r in referrers],
 "actual_repeat_orders":None,"actual_retention_rate":None,
 "actual_referral_conversions":None,"actual_revenue":None,
 "automatic_ordering_enabled":False,"points_enabled":False,"referral_rewards_enabled":False}

@router.get("/summary")
def customer_engagement_summary(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 loyalty=db.execute(text("SELECT COUNT(*) FROM marketing.loyalty_enrolments")).scalar_one()
 repeat=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='draft'")).scalar_one()
 cancelled=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='cancelled'")).scalar_one()
 approved=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='approved'")).scalar_one()
 rejected=db.execute(text("SELECT COUNT(*) FROM marketing.repeat_order_templates WHERE status='rejected'")).scalar_one()
 referrals=db.execute(text("SELECT COUNT(*) FROM marketing.referral_plans")).scalar_one()
 return {"draft_loyalty_enrolments":loyalty,"draft_repeat_order_templates":repeat,"cancelled_repeat_order_templates":cancelled,"approved_repeat_order_templates":approved,"rejected_repeat_order_templates":rejected,"draft_referrals":referrals,
 "points_enabled":False,"automatic_ordering_enabled":False,"referral_rewards_enabled":False}
