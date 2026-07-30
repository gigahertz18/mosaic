"""Application configuration.

Configuration is defined by strongly typed, immutable settings objects.
Values are supplied by the execution environment (Docker Compose locally,
the hosting platform's environment variables in staging/production, and
explicit construction in tests). This module is the *only* place in the
application allowed to read from ``os.environ`` (enforced by convention
and by the ``load_settings`` factory below).

No ``.env`` file and no ``python-dotenv`` dependency are used anywhere.
"""

from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache

from pydantic import BaseModel, Field


class Environment(StrEnum):
    """Deployment environment the application is running in."""

    LOCAL = "local"
    TEST = "test"
    CI = "ci"
    STAGING = "staging"
    PRODUCTION = "production"


class DatabaseSettings(BaseModel):
    """Connection settings for the primary PostgreSQL database."""

    model_config = {"frozen": True}

    host: str
    port: int = 5432
    user: str
    password: str
    name: str
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

    @property
    def async_dsn(self) -> str:
        """Return an asyncpg-compatible SQLAlchemy connection string."""
        return f"postgresql+asyncpg://{self.user}:{self.password}" f"@{self.host}:{self.port}/{self.name}"

    @property
    def sync_dsn(self) -> str:
        """Return a psycopg-compatible SQLAlchemy connection string.

        Used by Alembic, which drives migrations synchronously.
        """
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class ObjectStorageSettings(BaseModel):
    """Connection settings for the MinIO / S3-compatible object store."""

    model_config = {"frozen": True}

    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool = False


class LoggingSettings(BaseModel):
    """Structured logging configuration."""

    model_config = {"frozen": True}

    level: str = "INFO"
    json_format: bool = True


class Settings(BaseModel):
    """Root application settings.

    Immutable and hashable so it can be safely cached and shared as a
    FastAPI dependency across the lifetime of the process.
    """

    model_config = {"frozen": True}

    environment: Environment
    debug: bool = False
    app_name: str = "mosaic"
    api_prefix: str = "/api/v1"

    database: DatabaseSettings
    storage: ObjectStorageSettings
    logging: LoggingSettings = Field(default_factory=LoggingSettings)

    @property
    def is_local(self) -> bool:
        return self.environment == Environment.LOCAL

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION


class MissingEnvironmentVariableError(RuntimeError):
    """Raised when a required environment variable is not set."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Required environment variable '{name}' is not set")
        self.name = name


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise MissingEnvironmentVariableError(name)
    return value


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


def load_settings() -> Settings:
    """Build a :class:`Settings` instance from process environment variables.

    This is the single entry point through which the application reads
    ``os.environ``. Every other module receives configuration through
    dependency injection instead of reading the environment directly.
    """
    environment = Environment(_env("MOSAIC_ENVIRONMENT", Environment.LOCAL.value))

    database = DatabaseSettings(
        host=_require_env("MOSAIC_DB_HOST"),
        port=int(_env("MOSAIC_DB_PORT", "5432")),
        user=_require_env("MOSAIC_DB_USER"),
        password=_require_env("MOSAIC_DB_PASSWORD"),
        name=_require_env("MOSAIC_DB_NAME"),
        pool_size=int(_env("MOSAIC_DB_POOL_SIZE", "5")),
        max_overflow=int(_env("MOSAIC_DB_MAX_OVERFLOW", "10")),
        echo=_env("MOSAIC_DB_ECHO", "false").lower() == "true",
    )

    storage = ObjectStorageSettings(
        endpoint=_require_env("MOSAIC_STORAGE_ENDPOINT"),
        access_key=_require_env("MOSAIC_STORAGE_ACCESS_KEY"),
        secret_key=_require_env("MOSAIC_STORAGE_SECRET_KEY"),
        bucket=_env("MOSAIC_STORAGE_BUCKET", "mosaic"),
        secure=_env("MOSAIC_STORAGE_SECURE", "false").lower() == "true",
    )

    logging_settings = LoggingSettings(
        level=_env("MOSAIC_LOG_LEVEL", "INFO"),
        json_format=_env("MOSAIC_LOG_JSON", "true").lower() == "true",
    )

    return Settings(
        environment=environment,
        debug=_env("MOSAIC_DEBUG", "false").lower() == "true",
        app_name=_env("MOSAIC_APP_NAME", "mosaic"),
        api_prefix=_env("MOSAIC_API_PREFIX", "/api/v1"),
        database=database,
        storage=storage,
        logging=logging_settings,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide cached :class:`Settings` instance.

    Cached because ``Settings`` is frozen/hashable and safe to reuse; this
    keeps environment parsing to a single pass per process while still
    allowing tests to construct their own explicit ``Settings`` objects
    without going through this cache at all.
    """
    return load_settings()
