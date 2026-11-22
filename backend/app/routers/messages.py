from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CustomerMessage
from ..schemas import MessageCreate, MessageOut

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(data: MessageCreate, db: Session = Depends(get_db)):
    item = CustomerMessage(name=data.name.strip(), email=data.email.lower(), subject=data.subject.strip(), message=data.message.strip())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
