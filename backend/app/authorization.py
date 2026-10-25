"""Resolve staff authorisation before opening database connections."""
from fastapi import Depends
from .security import current_identity, require_staff


def staff_identity(identity: dict = Depends(current_identity)) -> dict:
    require_staff(identity)
    return identity
