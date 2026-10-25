"""Queue operational alerts for future externally configured delivery."""
from uuid import uuid4
from sqlalchemy import text
from sqlalchemy.orm import Session
def enqueue_pending(db:Session)->int:
 rows=db.execute(text("""SELECT a.id FROM finance.operational_alerts a
 LEFT JOIN finance.alert_outbox o ON o.alert_id=a.id
 WHERE o.id IS NULL ORDER BY a.created_at LIMIT 100""")).scalars().all()
 for alert_id in rows:
  db.execute(text("""INSERT INTO finance.alert_outbox (id,alert_id,channel,state)
  VALUES (:id,:alert,'email','pending') ON CONFLICT (alert_id) DO NOTHING"""),
  {"id":uuid4(),"alert":alert_id})
 db.commit()
 return len(rows)
