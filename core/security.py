from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from config import settings

# ── Password Hashing (Argon2id) ──

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2id."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hash."""
    return password_hasher.verify(plain_password, hashed_password)


# ── JWT Tokens ──

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    """Decode and verify a JWT access token. Returns payload or None."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        return None
