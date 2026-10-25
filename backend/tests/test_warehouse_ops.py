from fastapi.testclient import TestClient
from app.main import app

def test_warehouse_post_requires_auth():
    c=TestClient(app)
    assert c.get("/api/v1/admin/warehouse/movements").status_code==401
    assert c.post("/api/v1/admin/warehouse/receipts",json={
        "operation_key":"receipt-123456","warehouse_id":"00000000-0000-0000-0000-000000000001",
        "product_id":"00000000-0000-0000-0000-000000000002","quantity":10,"reference":"GRN-1"
    }).status_code==401

def test_zero_quantity_rejected():
    c=TestClient(app)
    assert c.post("/api/v1/admin/warehouse/receipts",json={
        "operation_key":"receipt-123456","warehouse_id":"00000000-0000-0000-0000-000000000001",
        "product_id":"00000000-0000-0000-0000-000000000002","quantity":0,"reference":"GRN-1"
    }).status_code==422
