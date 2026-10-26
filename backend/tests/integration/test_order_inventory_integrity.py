"""Real PostgreSQL quotation conversion invariants; all fixtures rollback."""
import os
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.orders import CreateOrder,create_order

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

@pytest.fixture
def order_db():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 conn=engine.connect()
 outer=conn.begin()
 db=Session(bind=conn,join_transaction_mode="create_savepoint")
 unique=uuid4().hex
 customer,product,book,quote,item,warehouse=(uuid4() for _ in range(6))
 try:
  db.execute(text("""INSERT INTO crm.customers(id,customer_number,customer_type,display_name)
  VALUES(:id,:code,'individual','Synthetic buyer')"""),{"id":customer,"code":"CI-"+unique[:20]})
  db.execute(text("""INSERT INTO catalog.products(id,sku,name)
  VALUES(:id,:sku,'Synthetic Makhulo')"""),{"id":product,"sku":"CI-"+unique[:20]})
  db.execute(text("""INSERT INTO pricing.price_books(id,code,name)
  VALUES(:id,:code,'CI price book')"""),{"id":book,"code":"CI-"+unique[:20]})
  db.execute(text("""INSERT INTO inventory.warehouses(id,code,name)
  VALUES(:id,:code,'Synthetic warehouse')"""),{"id":warehouse,"code":"CI-"+unique[:20]})
  db.execute(text("""INSERT INTO sales.quotations
  (id,quotation_number,customer_id,price_book_id,status,subtotal,created_by,expires_at)
  VALUES(:id,:code,:customer,:book,'draft',430,'ci',
  :expiry)"""),{"id":quote,"code":"CI-"+unique[:20],"customer":customer,"book":book,
   "expiry":datetime.now(timezone.utc)+timedelta(days=1)})
  db.execute(text("""INSERT INTO sales.quotation_items
  (id,quotation_id,product_id,sku_snapshot,product_name_snapshot,quantity,pricing_method_snapshot,line_total)
  VALUES(:id,:quote,:product,'CI-ITEM','Synthetic Makhulo',4,'fixed_bundle',430)"""),
  {"id":item,"quote":quote,"product":product})
  db.execute(text("""INSERT INTO inventory.stock_balances(warehouse_id,product_id,on_hand,reserved)
  VALUES(:warehouse,:product,5,0)"""),{"warehouse":warehouse,"product":product})
  db.commit()
  yield db,quote,warehouse,product
 finally:
  db.close()
  outer.rollback()
  conn.close()
  engine.dispose()

def snapshot(db,warehouse,product):
 return db.execute(text("""SELECT on_hand,reserved FROM inventory.stock_balances
 WHERE warehouse_id=:w AND product_id=:p"""),{"w":warehouse,"p":product}).one()

def test_success_and_duplicate_order_do_not_double_reserve(order_db):
 db,quote,warehouse,product=order_db
 args=CreateOrder(quotation_id=quote,warehouse_id=warehouse)
 result=create_order(args,{"sub":"ci-staff"},db)
 assert result["status"]=="pending_payment"
 assert result["payment_received"] is False
 assert tuple(snapshot(db,warehouse,product))==(5,4)
 with pytest.raises(HTTPException) as exc:
  create_order(args,{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(5,4)
 assert db.execute(text("SELECT COUNT(*) FROM sales.sales_orders WHERE quotation_id=:q"),{"q":quote}).scalar_one()==1

def test_shortage_rolls_back_all_reservations_and_order(order_db):
 db,quote,warehouse,product=order_db
 db.execute(text("""UPDATE inventory.stock_balances SET on_hand=3 WHERE warehouse_id=:w AND product_id=:p"""),
 {"w":warehouse,"p":product})
 db.commit()
 with pytest.raises(HTTPException) as exc:
  create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(3,0)
 assert db.execute(text("SELECT COUNT(*) FROM sales.sales_orders WHERE quotation_id=:q"),{"q":quote}).scalar_one()==0
