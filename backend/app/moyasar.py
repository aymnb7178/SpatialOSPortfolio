from fastapi import HTTPException


async def create_payment(*args, **kwargs) -> dict:
    """الدفع غير مفعّل في هذا المشروع؛ لا تُرسل بيانات بطاقة إلى أي مزود."""
    raise HTTPException(
        status_code=409,
        detail="الدفع تجريبي للعرض فقط وغير مفعّل؛ لم يتم إرسال أو حفظ أي بيانات بطاقة",
    )
