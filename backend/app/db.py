import os
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import HTTPException


@lru_cache
def engine():
    return create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)


def db_session():
    try:
        with Session(engine()) as session:
            yield session
    except KeyError:
        raise HTTPException(503, "Database not configured")
