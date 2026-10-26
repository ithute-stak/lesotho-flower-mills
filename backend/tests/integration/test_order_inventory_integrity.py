"""Real PostgreSQL quotation conversion invariants; all fixtures rollback."""
import os
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.orders import CreateOrder,create_order,cancel_unpaid_order

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

def test_cancel_releases_once_and_preserves_on_hand(order_db):
 db,quote,warehouse,product=order_db
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),
                    {"sub":"ci-staff"},db)
 assert tuple(snapshot(db,warehouse,product))==(5,4)
 result=cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert result["status"]=="cancelled"
 assert result["released_reservations"]==1
 assert tuple(snapshot(db,warehouse,product))==(5,0)
 with pytest.raises(HTTPException) as exc:
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(5,0)
 assert db.execute(text("""SELECT COUNT(*) FROM inventory.stock_reservations
  WHERE status='active' AND quotation_item_id IN
  (SELECT id FROM sales.quotation_items WHERE quotation_id=:q)"""),{"q":quote}).scalar_one()==0

def test_confirmed_order_cannot_cancel_or_release(order_db):
 db,quote,warehouse,product=order_db
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),
                    {"sub":"ci-staff"},db)
 db.execute(text("UPDATE sales.sales_orders SET status='confirmed' WHERE id=:id"),
            {"id":order["id"]})
 db.commit()
 with pytest.raises(HTTPException) as exc:
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(5,4)

def test_cancellation_records_single_immutable_audit_event(order_db):
 db,quote,warehouse,product=order_db
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),{"sub":"ci-staff"},db)
 cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 rows=db.execute(text("""SELECT actor_subject,released_count FROM sales.order_cancellation_events
 WHERE order_id=:order"""),{"order":order["id"]}).all()
 assert rows==[("ci-staff",1)]
 with pytest.raises(HTTPException):
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert db.execute(text("""SELECT COUNT(*) FROM sales.order_cancellation_events
 WHERE order_id=:order"""),{"order":order["id"]}).scalar_one()==1

def test_two_product_release_rolls_back_if_second_balance_is_missing(order_db):
 db,quote,warehouse,first_product=order_db
 second_product,second_item=uuid4(),uuid4()
 code="CI-"+uuid4().hex[:20]
 db.execute(text("INSERT INTO catalog.products(id,sku,name) VALUES (:id,:code,'Second synthetic bag')"),
            {"id":second_product,"code":code})
 db.execute(text("""INSERT INTO sales.quotation_items
 (id,quotation_id,product_id,sku_snapshot,product_name_snapshot,quantity,pricing_method_snapshot,line_total)
 VALUES (:id,:quote,:product,:sku,'Second synthetic bag',1,'fixed_bundle',100)"""),
 {"id":second_item,"quote":quote,"product":second_product,"sku":code})
 db.execute(text("""INSERT INTO inventory.stock_balances(warehouse_id,product_id,on_hand,reserved)
 VALUES (:w,:p,5,0)"""),{"w":warehouse,"p":second_product})
 db.commit()
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),{"sub":"ci-staff"},db)
 assert tuple(snapshot(db,warehouse,first_product))==(5,4)
 assert tuple(snapshot(db,warehouse,second_product))==(5,1)
 # Simulate a corrupt/missing reserved count after ordering, before cancellation.
 # The cancellation must fail and roll back any preceding released line.
 db.execute(text("""UPDATE inventory.stock_balances SET reserved=0
 WHERE warehouse_id=:w AND product_id=:p"""),{"w":warehouse,"p":second_product})
 db.commit()
 with pytest.raises(HTTPException) as exc:
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,first_product))==(5,4)
 assert db.execute(text("SELECT status FROM sales.sales_orders WHERE id=:id"),{"id":order["id"]}).scalar_one()=="pending_payment"
 assert db.execute(text("SELECT COUNT(*) FROM sales.order_cancellation_events WHERE order_id=:id"),{"id":order["id"]}).scalar_one()==0

def test_checkout_session_blocks_cancellation_and_preserves_reservations(order_db):
 db,quote,warehouse,product=order_db
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),
                    {"sub":"ci-staff"},db)
 checkout=uuid4()
 token=uuid4().hex
 db.execute(text("""INSERT INTO finance.checkout_sessions
 (id,sales_order_id,provider_session_id,idempotency_key,amount,created_by)
 VALUES (:id,:order,:provider,:key,430,'ci-staff')"""),
 {"id":checkout,"order":order["id"],"provider":"ci-"+token,"key":"ci-"+token})
 db.commit()
 with pytest.raises(HTTPException) as exc:
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(5,4)
 assert db.execute(text("SELECT status FROM sales.sales_orders WHERE id=:id"),{"id":order["id"]}).scalar_one()=="pending_payment"
 assert db.execute(text("SELECT COUNT(*) FROM sales.order_cancellation_events WHERE order_id=:id"),{"id":order["id"]}).scalar_one()==0

@pytest.mark.parametrize("record_type",["attempt","transaction"])
def test_financial_activity_blocks_cancellation(order_db,record_type):
 db,quote,warehouse,product=order_db
 order=create_order(CreateOrder(quotation_id=quote,warehouse_id=warehouse),{"sub":"ci-staff"},db)
 key=uuid4().hex
 if record_type=="attempt":
  db.execute(text("""INSERT INTO finance.checkout_attempts
   (id,sales_order_id,idempotency_key,state,amount,created_by)
   VALUES (:id,:order,:key,'initiating',430,'ci')"""),
   {"id":uuid4(),"order":order["id"],"key":key})
 else:
  db.execute(text("""INSERT INTO finance.payment_transactions
   (id,sales_order_id,provider,provider_reference,amount)
   VALUES (:id,:order,'sandbox',:reference,430)"""),
   {"id":uuid4(),"order":order["id"],"reference":key})
 db.commit()
 with pytest.raises(HTTPException) as exc:
  cancel_unpaid_order(order["id"],{"sub":"ci-staff"},db)
 assert exc.value.status_code==409
 assert tuple(snapshot(db,warehouse,product))==(5,4)
 assert db.execute(text("SELECT status FROM sales.sales_orders WHERE id=:id"),
                   {"id":order["id"]}).scalar_one()=="pending_payment"
