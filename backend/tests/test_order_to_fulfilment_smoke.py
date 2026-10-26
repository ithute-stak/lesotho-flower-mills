"""Synthetic order-to-fulfilment boundary test without payments or stock dispatch."""
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from fastapi import HTTPException
from app.orders import CreateOrder,create_order
from app.fulfilment import create_pick_list

class Result:
 def __init__(self,one=None,rows=None,rowcount=0):
  self._one=one;self._rows=rows or [];self.rowcount=rowcount
 def first(self):return self._one
 def mappings(self):return self
 def all(self):return self._rows

class SyntheticDb:
 def __init__(self,quote,warehouse,product,item):
  self.quote=quote;self.warehouse=warehouse;self.product=product;self.item=item
  self.available=10;self.reserved=0;self.order=None;self.commits=0
 def execute(self,statement,params=None):
  sql=str(statement);params=params or {}
  if "FROM sales.quotations" in sql:
   return Result({"id":self.quote,"customer_id":uuid4(),"subtotal":430,
                  "status":"draft","expires_at":datetime.now(timezone.utc)+timedelta(hours=1)})
  if "SELECT id FROM sales.sales_orders WHERE quotation_id" in sql:return Result()
  if "FROM sales.quotation_items WHERE quotation_id" in sql:
   return Result(rows=[{"id":self.item,"product_id":self.product,"quantity":1}])
  if "UPDATE inventory.stock_balances SET reserved" in sql:
   qty=params["qty"]
   if qty>self.available:return Result(rowcount=0)
   self.available-=qty;self.reserved+=qty
   return Result(rowcount=1)
  if "INSERT INTO sales.sales_orders" in sql:
   self.order={"id":params["id"],"status":"pending_payment","quotation_id":self.quote}
   return Result(rowcount=1)
  if "INSERT INTO inventory.stock_reservations" in sql:return Result(rowcount=1)
  if "FROM finance.checkout_sessions" in sql:return Result()
  if "FROM sales.sales_orders WHERE id" in sql:
   return Result(self.order)
  raise AssertionError("Unexpected SQL in synthetic workflow: "+sql[:130])
 def commit(self):self.commits+=1
 def rollback(self):self.order=None;self.reserved=0

def test_quote_conversion_reserves_stock_but_does_not_permit_picking():
 quote,warehouse,product,item=(uuid4() for _ in range(4))
 db=SyntheticDb(quote,warehouse,product,item)
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),
                    {"sub":"synthetic-staff","role":"admin"},db)
 assert order["status"]=="pending_payment"
 assert order["payment_received"] is False
 assert order["stock_reserved"] is True
 assert db.reserved==1 and db.available==9
 assert db.commits==1
 with pytest.raises(HTTPException) as exc:
  create_pick_list(db.order["id"],{"sub":"synthetic-staff","role":"admin"},db)
 assert exc.value.status_code==409
 assert db.commits==1
