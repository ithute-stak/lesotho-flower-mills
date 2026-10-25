"""Real PostgreSQL row-lock concurrency test with isolated CI fixture cleanup."""
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import Session
from app.stock import reserve_quantity

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="Postgres integration URL required")

def test_concurrent_reservations_cannot_oversell():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"],pool_size=3,max_overflow=1)
 warehouse,product=uuid4(),uuid4()
 unique=uuid4().hex[:15]
 try:
  with engine.begin() as con:
   con.execute(text("INSERT INTO inventory.warehouses(id,code,name) VALUES (:id,:code,'CI Warehouse')"),
               {"id":warehouse,"code":"CI-"+unique})
   con.execute(text("INSERT INTO catalog.products(id,sku,name) VALUES (:id,:sku,'CI Product')"),
               {"id":product,"sku":"CI-"+unique})
   con.execute(text("""INSERT INTO inventory.stock_balances(warehouse_id,product_id,on_hand,reserved)
   VALUES (:w,:p,5,0)"""),{"w":warehouse,"p":product})
  barrier=Barrier(2)
  def reserve():
   with Session(engine) as db:
    barrier.wait(timeout=15)
    success=reserve_quantity(db,warehouse,product,4)
    db.commit()
    return success
  with ThreadPoolExecutor(max_workers=2) as pool:
   first=pool.submit(reserve)
   second=pool.submit(reserve)
   assert sorted((first.result(timeout=20),second.result(timeout=20)))==[False,True]
  with engine.connect() as con:
   row=con.execute(text("""SELECT on_hand,reserved FROM inventory.stock_balances
    WHERE warehouse_id=:w AND product_id=:p"""),{"w":warehouse,"p":product}).one()
   assert row.on_hand==5
   assert row.reserved==4
 finally:
  with engine.begin() as con:
   con.execute(text("DELETE FROM inventory.stock_balances WHERE warehouse_id=:w AND product_id=:p"),{"w":warehouse,"p":product})
   con.execute(text("DELETE FROM catalog.products WHERE id=:p"),{"p":product})
   con.execute(text("DELETE FROM inventory.warehouses WHERE id=:w"),{"w":warehouse})
  engine.dispose()

def test_checkout_idempotency_database_constraint_present():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as conn:
   rows=conn.execute(text("""SELECT conname FROM pg_constraint
    WHERE conrelid='finance.checkout_sessions'::regclass AND contype='u'""")).scalars().all()
   assert any("idempotency_key" in name for name in rows)
   assert any("provider_session_id" in name for name in rows)
 finally:
  engine.dispose()
