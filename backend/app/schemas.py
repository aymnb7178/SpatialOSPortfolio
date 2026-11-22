from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

class MessageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    subject: str = Field(default="", max_length=200)
    message: str = Field(min_length=10, max_length=5000)

class MessageOut(MessageCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    created_at: datetime

class OrderCreate(BaseModel):
    service: str = Field(min_length=2, max_length=160)
    details: str = Field(default="", max_length=5000)

class OrderOut(OrderCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    created_at: datetime

class PaymentCreate(BaseModel):
    order_id: int
    amount: int = Field(gt=0, le=10_000_000)
    currency: str = Field(default="SAR", min_length=3, max_length=3)
    card_name: str = Field(min_length=5, max_length=255)
    card_number: str = Field(min_length=16, max_length=19)
    card_month: int = Field(ge=1, le=12)
    card_year: int = Field(ge=2024, le=2100)
    card_cvc: str = Field(min_length=3, max_length=4)

class PaymentOut(BaseModel):
    id: int
    status: str
    moyasar_id: str | None = None
    transaction_url: str | None = None
