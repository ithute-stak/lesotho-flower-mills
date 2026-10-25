from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.order_totals import calculate

def test_discount_freight_and_tax():
 result=calculate(Decimal("2000"),Decimal("100"),Decimal("75"),1500)
 assert result["taxable_base"]==Decimal("1900.00")
 assert result["tax_amount"]==Decimal("285.00")
 assert result["total"]==Decimal("2260.00")
def test_taxable_freight():
 result=calculate(Decimal("2000"),Decimal("0"),Decimal("100"),1500,True)
 assert result["total"]==Decimal("2415.00")
def test_excess_discount_rejected():
 with pytest.raises(ValueError):calculate(Decimal("430"),Decimal("500"),Decimal("0"),0)
def test_preview_requires_staff():
 response=TestClient(app).post("/api/v1/admin/orders/00000000-0000-0000-0000-000000000001/totals/preview",
 json={"tax_rate_bps":1500,"policy_reference":"example-policy"})
 assert response.status_code==401
