"""安全工具：JWT 签发/验证，手机号加密。"""
import base64
import hashlib
from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "refresh"},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def _get_fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest())
    return Fernet(key)


def encrypt_phone(phone: str) -> str:
    return _get_fernet().encrypt(phone.encode()).decode()


def decrypt_phone(encrypted: str) -> str:
    return _get_fernet().decrypt(encrypted.encode()).decode()
