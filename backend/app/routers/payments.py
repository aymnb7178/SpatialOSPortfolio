from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..config import get_settings
from ..database import get_db
from ..models import Order, Payment, User
from ..moyasar import create_payment
from ..schemas import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/create", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def start_payment(data: PaymentCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.scalar(select(Order).where(Order.id == data.order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(status_code=404, detail="الطلب غير موجود")
    payment = Payment(order_id=order.id, amount=data.amount, currency=data.currency.upper(), status="initiated")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    provider = await create_payment(given_id=str(uuid4()), amount=data.amount, currency=data.currency, description=f"SpatialOS order #{order.id}", callback_url=get_settings().moyasar_callback_url, card_name=data.card_name, card_number=data.card_number, card_month=data.card_month, card_year=data.card_year, card_cvc=data.card_cvc)
    payment.moyasar_id = provider.get("id")
    payment.status = provider.get("status", "initiated")
    payment.transaction_url = (provider.get("source") or {}).get("transaction_url")
    db.commit()
    db.refresh(payment)
    return payment

@router.post("/webhook", status_code=200)
async def moyasar_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    settings = get_settings()
    if settings.moyasar_webhook_secret and payload.get("secret_token") != settings.moyasar_webhook_secret:
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
    elif event_type == "payment_faild":
        status_value = "failed"
    elif event_type.startswith("payment_"):
        status_value = status_value or event_type.removeprefix("payment_")
    if status_value:
        payment.status = status_value
        if status_value == "paid":
            payment.order.status = "paid"
        db.commit()
    return {"received": True}
