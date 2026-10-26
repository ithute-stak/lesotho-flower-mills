"""Multi-connection PostgreSQL order locking regression tests."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.orders import CreateOrder,create_order,cancel_unpaid_order

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

@pytest.fixture
def committed_order():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"],pool_size=4)
 customer,product,book,quote,item,warehouse=(uuid4() for _ in range(6))
 unique=uuid4().hex[:20]
 try:
  with engine.begin() as db:
   db.execute(text("INSERT INTO crm.customers(id,customer_number,customer_type,display_name) VALUES (:id,:code,'individual','CI buyer')"),{"id":customer,"code":"CI-"+unique})
   db.execute(text("INSERT INTO catalog.products(id,sku,name) VALUES (:id,:code,'CI product')"),{"id":product,"code":"CI-"+unique})
   db.execute(text("INSERT INTO pricing.price_books(id,code,name) VALUES (:id,:code,'CI book')"),{"id":book,"code":"CI-"+unique})
   db.execute(text("INSERT INTO inventory.warehouses(id,code,name) VALUES (:id,:code,'CI warehouse')"),{"id":warehouse,"code":"CI-"+unique})
   db.execute(text("""INSERT INTO sales.quotations
    (id,quotation_number,customer_id,price_book_id,status,subtotal,created_by,expires_at)
    VALUES (:id,:code,:customer,:book,'draft',430,'ci',:expiry)"""),
    {"id":quote,"code":"CI-"+unique,"customer":customer,"book":book,"expiry":datetime.now(timezone.utc)+timedelta(days=1)})
   db.execute(text("""INSERT INTO sales.quotation_items
    (id,quotation_id,product_id,sku_snapshot,product_name_snapshot,quantity,pricing_method_snapshot,line_total)
    VALUES (:id,:quote,:product,'CI','CI product',4,'fixed_bundle',430)"""),{"id":item,"quote":quote,"product":product})
   db.execute(text("INSERT INTO inventory.stock_balances(warehouse_id,product_id,on_hand,reserved) VALUES (:w,:p,5,0)"),{"w":warehouse,"p":product})
  with Session(engine) as db:
   order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),{"sub":"ci-finance-admin"},db)
  yield engine,order["id"],warehouse,product
 finally:
  with engine.begin() as db:
   audited=db.execute(text("SELECT 1 FROM sales.order_cancellation_events WHERE order_id IN (SELECT id FROM sales.sales_orders WHERE quotation_id=:q)"),{"q":quote}).first()
   if audited is not None:
    # Immutable audit must not be bypassed; CI database is ephemeral.
    return
   db.execute(text("DELETE FROM inventory.stock_reservations WHERE quotation_item_id=:i"),{"i":item})
   db.execute(text("DELETE FROM sales.sales_orders WHERE quotation_id=:q"),{"q":quote})
   db.execute(text("DELETE FROM sales.quotation_items WHERE id=:i"),{"i":item})
   db.execute(text("DELETE FROM sales.quotations WHERE id=:q"),{"q":quote})
   db.execute(text("DELETE FROM inventory.stock_balances WHERE warehouse_id=:w AND product_id=:p"),{"w":warehouse,"p":product})
   db.execute(text("DELETE FROM inventory.warehouses WHERE id=:w"),{"w":warehouse})
   db.execute(text("DELETE FROM pricing.price_books WHERE id=:b"),{"b":book})
   db.execute(text("DELETE FROM catalog.products WHERE id=:p"),{"p":product})
   db.execute(text("DELETE FROM crm.customers WHERE id=:c"),{"c":customer})
  engine.dispose()

def test_two_simultaneous_cancellations_release_stock_only_once(committed_order):
 engine,order_id,warehouse,product=committed_order
 barrier=Barrier(2)
 def cancel():
  with Session(engine) as db:
   barrier.wait(timeout=15)
   try:
    cancel_unpaid_order(order_id,{"sub":"ci-finance-admin"},db)
    return "cancelled"
   except HTTPException as exc:
    db.rollback()
    return exc.status_code
 with ThreadPoolExecutor(max_workers=2) as pool:
  a=pool.submit(cancel);b=pool.submit(cancel)
  assert sorted((str(a.result(timeout=25)),str(b.result(timeout=25))))==["409","cancelled"]
 with engine.connect() as db:
  assert db.execute(text("SELECT reserved FROM inventory.stock_balances WHERE warehouse_id=:w AND product_id=:p"),{"w":warehouse,"p":product}).scalar_one()==0
  assert db.execute(text("SELECT COUNT(*) FROM sales.order_cancellation_events WHERE order_id=:id"),{"id":order_id}).scalar_one()==1

def test_order_lock_serializes_checkout_after_cancellation(committed_order):
 engine,order_id,warehouse,product=committed_order
 with Session(engine) as cancellation:
  cancellation.execute(text("SELECT id FROM sales.sales_orders WHERE id=:id FOR UPDATE"),{"id":order_id})
  with Session(engine) as checkout:
   checkout.execute(text("SET LOCAL lock_timeout='150ms'"))
   with pytest.raises(Exception):
    checkout.execute(text("SELECT id FROM sales.sales_orders WHERE id=:id FOR UPDATE"),{"id":order_id}).first()
   checkout.rollback()
  cancellation.rollback()
