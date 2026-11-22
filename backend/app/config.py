from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./spatialos-dev.db"
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440
    cookie_secure: bool = False
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    admin_email: str = ""
    admin_password_override: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    moyasar_secret_key: str = ""
    moyasar_webhook_secret: str = ""
    moyasar_live: bool = False
    moyasar_callback_url: str = "http://localhost:8000/payment/callback"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
