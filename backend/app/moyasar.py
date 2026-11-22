import httpx
from fastapi import HTTPException
from .config import get_settings

MOYASAR_URL = "https://api.moyasar.com/v1/payments"

async def create_payment(*, given_id: str, amount: int, currency: str, description: str, callback_url: str, card_name: str, card_number: str, card_month: int, card_year: int, card_cvc: str) -> dict:
    settings = get_settings()
    if not settings.moyasar_secret_key:
        raise HTTPException(status_code=503, detail="Moyasar غير مفعّل بعد؛ أضف المفتاح السري في البيئة")
    payload = {"given_id": given_id, "amount": amount, "currency": currency.upper(), "description": description, "callback_url": callback_url, "source": {"type": "creditcard", "name": card_name, "number": card_number, "month": card_month, "year": card_year, "cvc": card_cvc, "3ds": True}}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(MOYASAR_URL, json=payload, auth=(settings.moyasar_secret_key, ""))
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail={"message": "فشل إنشاء عملية الدفع", "provider": response.text[:500]})
    return response.json()
