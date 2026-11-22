from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models import User

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "role": user.role, "iat": now, "exp": now + timedelta(minutes=get_settings().jwt_expire_minutes)}
    return jwt.encode(payload, get_settings().jwt_secret, algorithm=ALGORITHM)


def get_current_user(access_token: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)) -> User:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="تسجيل الدخول مطلوب")
    try:
        payload = jwt.decode(access_token, get_settings().jwt_secret, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub", "0"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="جلسة الدخول غير صالحة") from None
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="الحساب غير متاح")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="صلاحية Admin مطلوبة")
    return user
