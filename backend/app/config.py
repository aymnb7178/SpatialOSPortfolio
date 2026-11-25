from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./spatialos-dev.db"
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440
    cookie_secure: bool = False
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    admin_email: str = ""
    moyasar_secret_key: str = ""
    moyasar_webhook_secret: str = ""
    moyasar_live: bool = False
    moyasar_callback_url: str = "http://localhost:8000/payment/callback"
    github_username: str = "aymnb7178"
    github_token: str = ""
    github_cache_ttl_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_production_security(self):
        if self.app_env.lower() == "production":
            if self.jwt_secret == "change-me-in-production" or len(self.jwt_secret) < 32:
                raise ValueError("JWT_SECRET must be a long random value in production")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true in production")
            if not self.admin_email.strip():
                raise ValueError("ADMIN_EMAIL must be configured in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
