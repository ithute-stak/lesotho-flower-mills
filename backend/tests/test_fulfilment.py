from fastapi.testclient import TestClient
from app.main import app

def test_pick_list_requires_auth():
    r=TestClient(app).post("/api/v1/admin/fulfilment/orders/00000000-0000-0000-0000-000000000001/pick-list")
    assert r.status_code==401

def test_loading_requires_auth():
    r=TestClient(app).post("/api/v1/admin/fulfilment/pick-lists/00000000-0000-0000-0000-000000000001/loading",json={
      "vehicle_registration":"ABC 123","driver_name":"Demo Driver",
      "items":[{"item_id":"00000000-0000-0000-0000-000000000002","quantity":10}]})
    assert r.status_code==401
