import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentriq"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Autonomous AI Security Operations Center (AI-SOC)"
    API_V1_PREFIX: str = "/api/v1"
    APP_ENV: str = "development"

    # Database Configuration (Docker Desktop PostgreSQL)
    POSTGRES_DB: str = "sentriq_soc"
    POSTGRES_USER: str = "sentriq_admin"
    POSTGRES_PASSWORD: str = "sentriq_secure_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://sentriq_admin:sentriq_secure_pass@localhost:5432/sentriq_soc"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://sentriq_admin:sentriq_secure_pass@localhost:5432/sentriq_soc"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Storage paths (project root Sentriq/)
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    MODELS_DIR: str = os.path.join(BASE_DIR, "models_store")
    DATA_DIR: str = os.path.join(BASE_DIR, "data")

    @validator("MODELS_DIR", pre=True)
    def resolve_models_dir(cls, v: str) -> str:
        if v:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            direct = os.path.join(base, "models_store")
            if os.path.exists(direct):
                return direct
        return v

    @validator("DATA_DIR", pre=True)
    def resolve_data_dir(cls, v: str) -> str:
        if v:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            direct = os.path.join(base, "data")
            if os.path.exists(direct):
                return direct
        return v

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

