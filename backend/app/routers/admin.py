from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import require_admin
from ..database import get_db
from ..models import CustomerMessage, Order, Payment, User
from ..schemas import MessageOut, OrderOut

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/summary")
def summary(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {"users": db.query(User).count(), "messages": db.query(CustomerMessage).count(), "orders": db.query(Order).count(), "payments": db.query(Payment).count()}

@router.get("/messages", response_model=list[MessageOut])
def messages(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(CustomerMessage).order_by(CustomerMessage.created_at.desc())))

@router.patch("/messages/{message_id}/status")
def update_message_status(message_id: int, status: str, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(CustomerMessage, message_id)
    if not item:
        raise HTTPException(status_code=404, detail="الرسالة غير موجودة")
    if status not in {"new", "read", "replied", "archived"}:
        raise HTTPException(status_code=400, detail="حالة غير صالحة")
    item.status = status
    db.commit()
    return {"id": item.id, "status": item.status}

@router.get("/orders", response_model=list[OrderOut])
def orders(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(Order).order_by(Order.created_at.desc())))

@router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(Order, order_id)
    if not item:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    if status not in {"pending", "in_progress", "paid", "completed", "cancelled"}:
        raise HTTPException(status_code=400, detail="حالة غير صالحة")
    item.status = status
    db.commit()
    return {"id": item.id, "status": item.status}

@router.get("/payments")
def payments(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [{"id": item.id, "order_id": item.order_id, "moyasar_id": item.moyasar_id, "amount": item.amount, "currency": item.currency, "status": item.status, "created_at": item.created_at} for item in db.scalars(select(Payment).order_by(Payment.created_at.desc()))]
