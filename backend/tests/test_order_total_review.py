from fastapi.testclient import TestClient
from app.main import app
def test_order_review_restricted():
 c=TestClient(app)
 assert c.post("/api/v1/admin/order-total-review/drafts",json={
 "order_id":"00000000-0000-0000-0000-000000000001","tax_rate_bps":0,"policy_reference":"draft-only"}).status_code==401
 assert c.get("/api/v1/admin/order-total-review/orders/00000000-0000-0000-0000-000000000001").status_code==401
