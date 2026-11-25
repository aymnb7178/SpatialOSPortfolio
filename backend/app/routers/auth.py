import time
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..auth import create_token, get_current_user, hash_password, verify_password
from ..config import get_settings
from ..database import get_db
from ..models import LoginEvent, User
from datetime import datetime, timezone
from ..schemas import LoginRequest, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
_auth_attempts: dict[str, list[float]] = {}
_AUTH_WINDOW_SECONDS = 15 * 60
_AUTH_MAX_ATTEMPTS = 10


def _check_auth_rate_limit(request: Request) -> None:
    now = time.monotonic()
    key = request.client.host if request.client else "unknown"
    recent = [stamp for stamp in _auth_attempts.get(key, []) if now - stamp < _AUTH_WINDOW_SECONDS]
    if len(recent) >= _AUTH_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="محاولات كثيرة؛ حاول بعد 15 دقيقة", headers={"Retry-After": str(_AUTH_WINDOW_SECONDS)})
    recent.append(now)
    _auth_attempts[key] = recent

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):
    _check_auth_rate_limit(request)
    email = data.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="البريد مستخدم مسبقاً")
    user = User(name=data.name.strip(), email=email, password_hash=hash_password(data.password), role="user")
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="البريد مستخدم مسبقاً") from None
    db.refresh(user)
    response.set_cookie("access_token", create_token(user), httponly=True, secure=get_settings().cookie_secure, samesite="lax", max_age=get_settings().jwt_expire_minutes * 60)
    return user

@router.post("/login", response_model=UserOut)
def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    _check_auth_rate_limit(request)
    email = data.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="البريد أو كلمة المرور غير صحيحة")
    user.last_login_at = datetime.now(timezone.utc)
    db.add(LoginEvent(user_id=user.id))
    db.commit()
    response.set_cookie("access_token", create_token(user), httponly=True, secure=get_settings().cookie_secure, samesite="lax", max_age=get_settings().jwt_expire_minutes * 60)
    return user

@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("access_token")

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
