from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..auth import require_admin
from ..database import get_db
from ..models import CustomerMessage, LoginEvent, Order, Payment, SiteLink, User, VisitEvent
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

@router.get("/users")
def users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [{"id": item.id, "name": item.name, "email": item.email, "role": item.role, "is_active": item.is_active, "created_at": item.created_at, "last_login_at": item.last_login_at} for item in db.scalars(select(User).order_by(User.created_at.desc()))]

@router.patch("/users/{user_id}/status")
def update_user_status(user_id: int, is_active: bool, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(User, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")
    if item.id == admin.id and not is_active:
        raise HTTPException(status_code=400, detail="لا يمكنك تعطيل حسابك")
    item.is_active = is_active
    db.commit()
    return {"id": item.id, "is_active": item.is_active}

@router.get("/login-events")
def login_events(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(select(LoginEvent, User).join(User, LoginEvent.user_id == User.id).order_by(LoginEvent.created_at.desc()).limit(100)).all()
    return [{"id": event.id, "user_id": user.id, "name": user.name, "email": user.email, "created_at": event.created_at} for event, user in rows]

@router.get("/visits")
def visits(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(VisitEvent.id))) or 0
    unique_sessions = db.scalar(select(func.count(func.distinct(VisitEvent.session_key)))) or 0
    recent = db.scalars(select(VisitEvent).order_by(VisitEvent.created_at.desc()).limit(100))
    return {"total": total, "unique_sessions": unique_sessions, "recent": [{"path": item.path, "session_key": item.session_key, "user_agent": item.user_agent, "created_at": item.created_at} for item in recent]}

@router.get("/links")
def links(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return [{"id": item.id, "label": item.label, "url": item.url, "channel": item.channel, "is_active": item.is_active, "sort_order": item.sort_order} for item in db.scalars(select(SiteLink).order_by(SiteLink.sort_order, SiteLink.id))]

@router.post("/links", status_code=201)
def create_link(data: dict, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = SiteLink(label=str(data.get("label", "")).strip()[:120], url=str(data.get("url", "")).strip()[:1000], channel=str(data.get("channel", "other"))[:40], sort_order=int(data.get("sort_order", 0)))
    if not item.label or not item.url:
        raise HTTPException(status_code=422, detail="اسم الرابط والعنوان مطلوبان")
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "label": item.label, "url": item.url, "channel": item.channel, "is_active": item.is_active, "sort_order": item.sort_order}

@router.patch("/links/{link_id}")
def update_link(link_id: int, data: dict, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(SiteLink, link_id)
    if not item:
        raise HTTPException(status_code=404, detail="الرابط غير موجود")
    for field in ("label", "url", "channel"):
        if field in data:
            setattr(item, field, str(data[field]).strip())
    if "is_active" in data:
        item.is_active = bool(data["is_active"])
    if "sort_order" in data:
        item.sort_order = int(data["sort_order"])
    db.commit()
    return {"id": item.id, "label": item.label, "url": item.url, "channel": item.channel, "is_active": item.is_active, "sort_order": item.sort_order}

@router.delete("/links/{link_id}", status_code=204)
def delete_link(link_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    item = db.get(SiteLink, link_id)
    if not item:
        raise HTTPException(status_code=404, detail="الرابط غير موجود")
    db.delete(item)
    db.commit()
