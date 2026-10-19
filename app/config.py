from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Plus UAE × Vortexen AI Sales Academy"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    SECRET_KEY: str = "plusuae-vortexen-secure-local-dev-secret-key-32bytes-min-length"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    INVITATION_EXPIRE_HOURS: int = 72
    
    DATABASE_URL: str = "sqlite:///./sales_academy.db"
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000,http://127.0.0.1:8001"
    
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_WINDOW_MINUTES: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def effective_database_url(self) -> str:
        url = self.DATABASE_URL
        if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
            url = "sqlite:////tmp/sales_academy.db"
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()

