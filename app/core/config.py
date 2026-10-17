"""Application configuration settings using Pydantic Settings."""

import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Info
    PROJECT_NAME: str = "Voice of Store Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./voice_of_store.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            # Render and some cloud providers provide "postgres://" or "postgresql://"
            # SQLAlchemy 2.x with psycopg 3 prefers "postgresql+psycopg://"
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+psycopg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+"):
                return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    # Security & JWT
    SECRET_KEY: str = "DEVELOPMENT_INSECURE_SECRET_KEY_REPLACE_IN_PRODUCTION_64CHAR"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Operational limits & Rate Limiting
    MAX_REQUEST_BODY_BYTES: int = 2 * 1024 * 1024  # 2MB
    RATE_LIMIT_PER_MINUTE: int = 120

    # ML & Policy Versions
    MODEL_VERSION: str = "v1.0.0-tfidf-linear"
    POLICY_VERSION: str = "v1.2.0-deterministic"
    MODEL_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")

    # Initial superadmin credentials (optional bootstrap)
    INITIAL_ADMIN_EMAIL: str = "admin@voiceofstore.internal"
    INITIAL_ADMIN_PASSWORD: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
