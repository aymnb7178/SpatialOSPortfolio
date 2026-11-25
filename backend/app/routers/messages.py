import time
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CustomerMessage
from ..schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["messages"])
_message_attempts: dict[str, list[float]] = {}
_MESSAGE_WINDOW_SECONDS = 15 * 60
_MESSAGE_MAX_ATTEMPTS = 20


def _check_message_rate_limit(request: Request) -> None:
    now = time.monotonic()
    key = request.client.host if request.client else "unknown"
    recent = [stamp for stamp in _message_attempts.get(key, []) if now - stamp < _MESSAGE_WINDOW_SECONDS]
    if len(recent) >= _MESSAGE_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="تم تجاوز حد الرسائل؛ حاول بعد 15 دقيقة", headers={"Retry-After": str(_MESSAGE_WINDOW_SECONDS)})
    recent.append(now)
    _message_attempts[key] = recent

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(data: MessageCreate, request: Request, db: Session = Depends(get_db)):
    _check_message_rate_limit(request)
    item = CustomerMessage(name=data.name.strip(), email=data.email.lower(), subject=data.subject.strip(), message=data.message.strip())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
