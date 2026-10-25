"""PostgreSQL integration checks, executed only with LFM_TEST_DATABASE_URL."""
import os
from uuid import uuid4
from decimal import Decimal
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.exc import DBAPIError

pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL test database not configured")

@pytest.fixture
def conn():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 with engine.connect() as connection:
  transaction=connection.begin()
  try:
   yield connection
  finally:
   transaction.rollback()
 engine.dispose()

def test_financial_migrations_present(conn):
 tables=conn.execute(text("""SELECT table_schema,table_name FROM information_schema.tables
 WHERE (table_schema='finance' AND table_name IN ('order_totals','financial_policies','total_review_events','checkout_sessions'))
 OR (table_schema='delivery' AND table_name IN ('tariffs','assignments'))""")).all()
 assert len(tables)==6

def test_policy_maker_checker_database_constraint(conn):
 # Isolated rolled-back changes; no durable testing data.
 pid=uuid4()
 with pytest.raises(DBAPIError):
  with conn.begin_nested():
   conn.execute(text("""INSERT INTO finance.financial_policies
   (id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps,status,created_by,approved_by)
   VALUES (:id,:code,1,0,false,0,'draft','same','same')"""),
   {"id":pid,"code":"CI-"+pid.hex[:20]})

def test_approved_policy_is_immutable(conn):
 pid=uuid4()
 conn.execute(text("""INSERT INTO finance.financial_policies
 (id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps,status,created_by,approved_by,effective_from)
 VALUES (:id,:code,1,0,false,0,'approved','maker','checker',now())"""),
 {"id":pid,"code":"CI-"+pid.hex[:20]})
 with pytest.raises(DBAPIError):
  with conn.begin_nested():
   conn.execute(text("UPDATE finance.financial_policies SET tax_rate_bps=100 WHERE id=:id"),{"id":pid})
 with pytest.raises(DBAPIError):
  with conn.begin_nested():
   conn.execute(text("DELETE FROM finance.financial_policies WHERE id=:id"),{"id":pid})

def test_failed_statement_rolls_back_only_to_savepoint(conn):
 pid=uuid4()
 conn.execute(text("""INSERT INTO finance.financial_policies
 (id,code,version,tax_rate_bps,delivery_taxable,max_discount_bps,status,created_by)
 VALUES (:id,:code,1,0,false,0,'draft','maker')"""),
 {"id":pid,"code":"CI-"+pid.hex[:20]})
 with pytest.raises(DBAPIError):
  with conn.begin_nested():
   conn.execute(text("UPDATE finance.financial_policies SET approved_by='maker' WHERE id=:id"),{"id":pid})
 row=conn.execute(text("SELECT status,approved_by FROM finance.financial_policies WHERE id=:id"),{"id":pid}).one()
 assert row.status=="draft"
 assert row.approved_by is None

def test_financial_audit_trigger_is_installed(conn):
 triggers=conn.execute(text("""SELECT tgname FROM pg_trigger
 WHERE tgrelid='finance.total_review_events'::regclass AND NOT tgisinternal""")).scalars().all()
 assert "trg_total_audit_immutable" in triggers
