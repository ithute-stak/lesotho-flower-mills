from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.quotations import QuotationCreate

def test_quotation_requires_staff():
    resp=TestClient(app).post("/api/v1/admin/quotations",json={
      "customer_id":"00000000-0000-0000-0000-000000000001",
      "price_book_id":"00000000-0000-0000-0000-000000000002",
      "items":[{"product_id":"00000000-0000-0000-0000-000000000003","quantity":5}]})
    assert resp.status_code==401

def test_quotation_requires_positive_quantity():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        QuotationCreate(customer_id=UUID(int=1),price_book_id=UUID(int=2),
          items=[{"product_id":str(UUID(int=3)),"quantity":0}])
