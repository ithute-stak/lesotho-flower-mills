"""Read-only, non-financial wholesale promotion planning statistics."""
from fastapi import APIRouter,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from .db import db_session
from .finance_permissions import finance_read
router=APIRouter(prefix="/api/v1/admin/wholesale-promotion-reports",tags=["wholesale-promotion-reports"])

@router.get("/summary")
def wholesale_promotion_summary(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT t.status,COUNT(*) AS tier_count,
 COUNT(DISTINCT t.campaign_id) AS campaign_count,
 COUNT(DISTINCT t.product_id) AS product_count,
 MIN(t.minimum_quantity) AS minimum_quantity,
 MAX(t.minimum_quantity) AS maximum_quantity
 FROM marketing.wholesale_discount_tiers t GROUP BY t.status ORDER BY t.status""")).mappings().all()
 summary=[{"status":r["status"],"tier_count":r["tier_count"],
 "campaign_count":r["campaign_count"],"product_count":r["product_count"],
 "minimum_quantity":r["minimum_quantity"],"maximum_quantity":r["maximum_quantity"]} for r in rows]
 return {"basis":"administrative_plans_only","currency":"LSL","checkout_enabled":False,
 "actual_redemptions":None,"actual_discount_amount":None,"actual_incremental_revenue":None,
 "groups":summary,"total_tiers":sum(r["tier_count"] for r in summary)}

@router.get("/campaigns")
def wholesale_promotion_campaign_report(identity:dict=Depends(finance_read),db:Session=Depends(db_session)):
 rows=db.execute(text("""SELECT t.campaign_id,c.code AS campaign_code,c.status AS campaign_status,
 COUNT(*) AS tier_count,COUNT(*) FILTER(WHERE t.status='approved') AS approved_tiers,
 COUNT(DISTINCT t.product_id) AS product_count
 FROM marketing.wholesale_discount_tiers t JOIN marketing.campaigns c ON c.id=t.campaign_id
 GROUP BY t.campaign_id,c.code,c.status ORDER BY c.code LIMIT 200""")).mappings().all()
 return {"basis":"administrative_plans_only","items":[dict(r) for r in rows],"checkout_enabled":False}
