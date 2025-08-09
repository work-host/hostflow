from datetime import datetime, timedelta, timezone
from typing import Optional, Iterable
import os
from jose import jwt
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(sub: str, extra: Optional[dict] = None) -> str:
    to_encode = {"sub": sub, "iat": datetime.now(timezone.utc)}
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRES_MIN)
    if extra:
        to_encode.update(extra)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def has_any_role(user_role: str, allowed: Iterable[str]) -> bool:
    return user_role in set(allowed)
