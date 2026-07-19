"""
AIgnition Backend — Configuration
Reads settings from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────
    APP_NAME: str = "AIgnition API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Server ────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ─────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── Storage ──────────────────────────────────────────────────────────
    UPLOADS_DIR: str = "app/storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── ML Interface ─────────────────────────────────────────────────────
    # Set to True to use fallback mock data when ML raises NotImplementedError
    ML_FALLBACK_ENABLED: bool = True

    # ── Report ───────────────────────────────────────────────────────────
    REPORT_COMPANY_NAME: str = "AIgnition"


settings = Settings()
