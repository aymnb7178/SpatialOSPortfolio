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


class ProjectBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=160)
    title_ar: str = Field(default="", max_length=160)
    eyebrow: str = Field(default="", max_length=120)
    category: str = Field(default="", max_length=80)
    summary: str = Field(default="", max_length=3000)
    summary_ar: str = Field(default="", max_length=3000)
    overview: str = Field(default="", max_length=8000)
    overview_ar: str = Field(default="", max_length=8000)
    problem: str = Field(default="", max_length=8000)
    problem_ar: str = Field(default="", max_length=8000)
    solution: str = Field(default="", max_length=8000)
    solution_ar: str = Field(default="", max_length=8000)
    features: list[str] = Field(default_factory=list, max_length=30)
    technologies: list[str] = Field(default_factory=list, max_length=30)
    architecture: str = Field(default="", max_length=8000)
    architecture_ar: str = Field(default="", max_length=8000)
    challenges: str = Field(default="", max_length=8000)
    challenges_ar: str = Field(default="", max_length=8000)
    results: str = Field(default="", max_length=8000)
    results_ar: str = Field(default="", max_length=8000)
    hero_media_url: str = Field(default="", max_length=1000)
    media_urls: list[str] = Field(default_factory=list, max_length=20)
    github_url: str = Field(default="", max_length=1000)
    demo_url: str = Field(default="", max_length=1000)
    related_slugs: list[str] = Field(default_factory=list, max_length=10)
    is_featured: bool = False
    is_visible: bool = True
    sort_order: int = Field(default=0, ge=-10000, le=10000)

    @field_validator("hero_media_url", "github_url", "demo_url")
    @classmethod
    def validate_optional_url(cls, value: str) -> str:
        value = value.strip()
        if value and not value.startswith(("https://", "http://", "/")):
            raise ValueError("الرابط يجب أن يبدأ بـ http أو https أو /")
        return value

    @field_validator("media_urls")
    @classmethod
    def validate_media_urls(cls, values: list[str]) -> list[str]:
        clean = []
        for value in values:
            value = value.strip()
            if value and (value.startswith(("https://", "http://", "/"))):
                clean.append(value)
            elif value:
                raise ValueError("روابط الوسائط غير صالحة")
        return clean

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=160)
    title_ar: str | None = Field(default=None, max_length=160)
    eyebrow: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=80)
    summary: str | None = Field(default=None, max_length=3000)
    summary_ar: str | None = Field(default=None, max_length=3000)
    overview: str | None = Field(default=None, max_length=8000)
    overview_ar: str | None = Field(default=None, max_length=8000)
    problem: str | None = Field(default=None, max_length=8000)
    problem_ar: str | None = Field(default=None, max_length=8000)
    solution: str | None = Field(default=None, max_length=8000)
    solution_ar: str | None = Field(default=None, max_length=8000)
    features: list[str] | None = Field(default=None, max_length=30)
    technologies: list[str] | None = Field(default=None, max_length=30)
    architecture: str | None = Field(default=None, max_length=8000)
    architecture_ar: str | None = Field(default=None, max_length=8000)
    challenges: str | None = Field(default=None, max_length=8000)
    challenges_ar: str | None = Field(default=None, max_length=8000)
    results: str | None = Field(default=None, max_length=8000)
    results_ar: str | None = Field(default=None, max_length=8000)
    hero_media_url: str | None = Field(default=None, max_length=1000)
    media_urls: list[str] | None = Field(default=None, max_length=20)
    github_url: str | None = Field(default=None, max_length=1000)
    demo_url: str | None = Field(default=None, max_length=1000)
    related_slugs: list[str] | None = Field(default=None, max_length=10)
    is_featured: bool | None = None
    is_visible: bool | None = None
    sort_order: int | None = Field(default=None, ge=-10000, le=10000)

    @field_validator("hero_media_url", "github_url", "demo_url")
    @classmethod
    def validate_optional_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if value and not value.startswith(("https://", "http://", "/")):
            raise ValueError("الرابط يجب أن يبدأ بـ http أو https أو /")
        return value

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    title_ar: str
    eyebrow: str
    category: str
    summary: str
    summary_ar: str
    overview: str
    overview_ar: str
    problem: str
    problem_ar: str
    solution: str
    solution_ar: str
    features: list[str]
    technologies: list[str]
    architecture: str
    architecture_ar: str
    challenges: str
    challenges_ar: str
    results: str
    results_ar: str
    hero_media_url: str
    media_urls: list[str]
    github_url: str
    demo_url: str
    related_slugs: list[str]
    is_featured: bool
    is_visible: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime


class GithubRepositoryAdminUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    is_featured: bool | None = None
    is_visible: bool | None = None
    sort_order: int | None = Field(default=None, ge=-10000, le=10000)

class CareerBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str = Field(default="experience", min_length=2, max_length=40)
    period: str = Field(default="", max_length=120)
    title: str = Field(min_length=1, max_length=200)
    title_ar: str = Field(default="", max_length=200)
    organization: str = Field(default="", max_length=200)
    organization_ar: str = Field(default="", max_length=200)
    description: str = Field(default="", max_length=5000)
    description_ar: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list, max_length=20)
    related_projects: list[str] = Field(default_factory=list, max_length=10)
    sort_order: int = Field(default=0, ge=-10000, le=10000)
    is_visible: bool = True

class CareerCreate(CareerBase):
    pass

class CareerUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: str | None = Field(default=None, min_length=2, max_length=40)
    period: str | None = Field(default=None, max_length=120)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    title_ar: str | None = Field(default=None, max_length=200)
    organization: str | None = Field(default=None, max_length=200)
    organization_ar: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    description_ar: str | None = Field(default=None, max_length=5000)
    tags: list[str] | None = Field(default=None, max_length=20)
    related_projects: list[str] | None = Field(default=None, max_length=10)
    sort_order: int | None = Field(default=None, ge=-10000, le=10000)
    is_visible: bool | None = None

class CareerOut(CareerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class SkillBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    name_ar: str = Field(default="", max_length=120)
    category: str = Field(default="technology", min_length=2, max_length=80)
    category_ar: str = Field(default="", max_length=80)
    level: int = Field(default=50, ge=0, le=100)
    description: str = Field(default="", max_length=2000)
    description_ar: str = Field(default="", max_length=2000)
    related_projects: list[str] = Field(default_factory=list, max_length=10)
    related_certificates: list[str] = Field(default_factory=list, max_length=10)
    sort_order: int = Field(default=0, ge=-10000, le=10000)
    is_visible: bool = True

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = Field(default=None, min_length=1, max_length=120)
    name_ar: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    category_ar: str | None = Field(default=None, max_length=80)
    level: int | None = Field(default=None, ge=0, le=100)
    description: str | None = Field(default=None, max_length=2000)
    description_ar: str | None = Field(default=None, max_length=2000)
    related_projects: list[str] | None = Field(default=None, max_length=10)
    related_certificates: list[str] | None = Field(default=None, max_length=10)
    sort_order: int | None = Field(default=None, ge=-10000, le=10000)
    is_visible: bool | None = None

class SkillOut(SkillBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
