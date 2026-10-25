import os
import pytest
from sqlalchemy import create_engine,text
pytestmark=pytest.mark.skipif(not os.getenv("LFM_TEST_DATABASE_URL"),reason="PostgreSQL required")

def test_competing_reconcilers_cannot_acquire_same_lock():
 engine=create_engine(os.environ["LFM_TEST_DATABASE_URL"])
 try:
  with engine.connect() as first,engine.connect() as second:
   with first.begin():
    assert first.execute(text("SELECT pg_try_advisory_xact_lock(53712036)")).scalar_one() is True
    with second.begin():
     assert second.execute(text("SELECT pg_try_advisory_xact_lock(53712036)")).scalar_one() is False
 finally:
  engine.dispose()
