"""Password hashing and signed API tokens."""
import os
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Header, HTTPException
from jwt import InvalidTokenError

ph = PasswordHasher()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    if len(password) < 12 or len(password) > 256:
        raise ValueError("password must contain 12–256 characters")
    return ph.hash(password)


def verify_password(encoded: str, password: str) -> bool:
    try:
        return ph.verify(encoded, password)
    except (VerifyMismatchError, VerificationError):
        return False


def create_token(subject: str, role: str) -> str:
    secret = os.environ.get("AUTH_SECRET")
    if not secret or len(secret) < 32:
        raise RuntimeError("AUTH_SECRET must have at least 32 characters")
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": subject, "role": role, "iat": now, "exp": now + timedelta(minutes=30)}, secret, algorithm=ALGORITHM)


def current_identity(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    secret = os.environ.get("AUTH_SECRET")
    if not secret or len(secret) < 32:
        raise HTTPException(503, "Authentication not configured")
    try:
        payload = jwt.decode(authorization[7:], secret, algorithms=[ALGORITHM], options={"require": ["sub", "exp"]})
        if not payload.get("sub"):
            raise InvalidTokenError("Missing subject")
        return payload
    except InvalidTokenError:
        raise HTTPException(401, "Invalid or expired token")


def require_staff(identity: dict) -> None:
    if identity.get("role") not in {"admin", "sales_manager"}:
        raise HTTPException(403, "Staff authorisation required")
