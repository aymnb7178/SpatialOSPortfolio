from secrets import compare_digest
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..config import get_settings
from ..database import get_db
from ..models import Order, Payment, User
from ..schemas import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def start_payment(data: PaymentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.id == data.order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    raise HTTPException(status_code=409, detail="الدفع تجريبي للعرض فقط وغير مفعّل؛ لم يتم إرسال أو حفظ أي بيانات بطاقة")

@router.post("/webhook", status_code=200)
async def moyasar_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    settings = get_settings()
    if not settings.moyasar_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook الدفع غير مهيأ")
    if not compare_digest(str(payload.get("secret_token", "")), settings.moyasar_webhook_secret):
        raise HTTPException(status_code=401, detail="Webhook secret غير صحيح")
    event_type = payload.get("type", "")
    provider_payment = payload.get("data") or {}
    provider_id = provider_payment.get("id")
    if not provider_id:
        return {"received": True}
    payment = db.scalar(select(Payment).where(Payment.moyasar_id == provider_id))
    if not payment:
        return {"received": True}
    status_value = provider_payment.get("status")
    if event_type == "payment_paid":
        status_value = "paid"
    elif event_type in {"payment_failed", "payment_faild"}:
        status_value = "failed"
    elif event_type.startswith("payment_"):
        status_value = status_value or event_type.removeprefix("payment_")
    if status_value:
        payment.status = status_value
        if status_value == "paid":
            payment.order.status = "paid"
        db.commit()
    return {"received": True}
