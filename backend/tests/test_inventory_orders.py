import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.stock import reserve_quantity

class FakeResult:
    def __init__(self, changed):
        self.rowcount=changed

class FakeSession:
    def __init__(self,available):
        self.available=available
    def execute(self,statement,params):
        if self.available>=params["qty"]:
            self.available-=params["qty"]
            return FakeResult(1)
        return FakeResult(0)

def test_reservation_rejects_insufficient_quantity():
    from uuid import UUID
    db=FakeSession(5)
    ident=UUID(int=1)
    assert reserve_quantity(db,ident,ident,4)
    assert not reserve_quantity(db,ident,ident,4)
    assert db.available==1

def test_reservation_rejects_zero():
    from uuid import UUID
    with pytest.raises(ValueError):
        reserve_quantity(FakeSession(20),UUID(int=1),UUID(int=2),0)

def test_order_api_rejects_public_access():
    c=TestClient(app)
    assert c.post("/api/v1/admin/orders",json={"quotation_id":"00000000-0000-0000-0000-000000000001","warehouse_id":"00000000-0000-0000-0000-000000000002"}).status_code==401
