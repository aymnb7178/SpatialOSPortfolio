from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

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
    model_config = ConfigDict(extra="forbid")
    order_id: int

class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    moyasar_id: str | None = None
    transaction_url: str | None = None

class SiteLinkCreate(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    url: str = Field(min_length=1, max_length=1000)
    channel: str = Field(default="other", min_length=1, max_length=40)
    sort_order: int = Field(default=0, ge=-10000, le=10000)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("https://", "http://", "mailto:")):
            raise ValueError("الرابط يجب أن يبدأ بـ http أو https أو mailto")
        return value

class SiteLinkUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, min_length=1, max_length=1000)
    channel: str | None = Field(default=None, min_length=1, max_length=40)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=-10000, le=10000)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value.startswith(("https://", "http://", "mailto:")):
            raise ValueError("الرابط يجب أن يبدأ بـ http أو https أو mailto")
        return value
