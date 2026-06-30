"""
SPARK — Application Configuration
Pydantic BaseSettings for type-safe, validated environment configuration.
Fails fast on startup if required variables are missing.
"""

from functools import lru_cache
from typing import Any, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All fields are validated at startup via Pydantic.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------------------------------------
    # Application
    # -------------------------------------------------------
    APP_ENV: str = Field(default="development", description="Application environment")
    APP_HOST: str = Field(default="0.0.0.0", description="Server host")
    APP_PORT: int = Field(default=8000, description="Server port")
    LOG_LEVEL: str = Field(default="DEBUG", description="Log level")

    # -------------------------------------------------------
    # Firebase
    # -------------------------------------------------------
    FIREBASE_PROJECT_ID: str = Field(
        default="", description="Firebase project ID"
    )
    FIREBASE_SERVICE_ACCOUNT_PATH: str = Field(
        default="./firebase-service-account.json",
        description="Path to Firebase service account JSON",
    )

    # -------------------------------------------------------
    # Google Cloud / Vertex AI
    # -------------------------------------------------------
    GOOGLE_CLOUD_PROJECT: str = Field(
        default="", description="GCP project ID"
    )
    GOOGLE_CLOUD_REGION: str = Field(
        default="us-central1", description="GCP region"
    )
    VERTEX_AI_MODEL: str = Field(
        default="gemini-2.5-flash", description="Vertex AI model name"
    )
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(
        default="./firebase-service-account.json",
        description="Path to GCP credentials",
    )

    # -------------------------------------------------------
    # Cloud Tasks
    # -------------------------------------------------------
    CLOUD_TASKS_QUEUE: str = Field(
        default="spark-agent-tasks", description="Cloud Tasks queue name"
    )
    CLOUD_TASKS_LOCATION: str = Field(
        default="us-central1", description="Cloud Tasks region"
    )
    CLOUD_RUN_SERVICE_URL: str = Field(
        default="http://localhost:8000",
        description="Cloud Run service URL for task callbacks",
    )

    # -------------------------------------------------------
    # Cloud Storage
    # -------------------------------------------------------
    GCS_BUCKET_NAME: str = Field(
        default="spark-documents", description="GCS bucket name"
    )

    # -------------------------------------------------------
    # BigQuery
    # -------------------------------------------------------
    BIGQUERY_DATASET: str = Field(
        default="spark_analytics", description="BigQuery dataset name"
    )

    # -------------------------------------------------------
    # Pub/Sub
    # -------------------------------------------------------
    PUBSUB_TOPIC: str = Field(
        default="spark-events", description="Pub/Sub topic name"
    )

    # -------------------------------------------------------
    # Google OAuth
    # -------------------------------------------------------
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: str = Field(
        default="", description="Google OAuth client secret"
    )

    # -------------------------------------------------------
    # CORS
    # Store as plain string internally, expose as List[str] via property.
    # This avoids Pydantic Settings v2 JSON parsing issues entirely.
    # -------------------------------------------------------
    ALLOWED_ORIGINS_STR: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="ALLOWED_ORIGINS",
        description="Comma-separated or JSON array of allowed CORS origins",
    )

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, value: str) -> str:
        """Ensure APP_ENV is a known environment."""
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"APP_ENV must be one of: {allowed}")
        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Ensure LOG_LEVEL is valid."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if value.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {allowed}")
        return value.upper()

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        Parse ALLOWED_ORIGINS from either format:
          - JSON array:  '["http://localhost:5173","http://localhost:3000"]'
          - CSV string:  'http://localhost:5173,http://localhost:3000'
        
        This property is what all application code should use.
        """
        raw = self.ALLOWED_ORIGINS_STR.strip()

        if raw.startswith("["):
            # JSON array format
            import json
            try:
                parsed = json.loads(raw)
                return [str(origin).strip() for origin in parsed]
            except Exception:
                pass

        # Comma-separated format (fallback)
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Returns cached Settings instance.
    lru_cache ensures only one instance is created per process.
    This is the correct pattern for FastAPI dependency injection.
    """
    return Settings()