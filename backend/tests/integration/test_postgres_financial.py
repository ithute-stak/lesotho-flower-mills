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
  with connection.begin():
   yield connection
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
