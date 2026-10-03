from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY_ACCESS_API, algorithm=ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@lru_cache(maxsize=1)
def get_dummy_hash() -> str:
    """Hash verified against when the account does not exist, so login takes the
    same time either way (prevents discovering registered emails by timing).
    Computed lazily so importing this module never depends on the hash backend."""
    return get_password_hash("not-a-real-password")
