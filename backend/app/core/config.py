from pydantic_settings import BaseSettings
from typing import List
from loguru import logger
from typing import Annotated, Any, Literal
import os
import sys

from pydantic import (
    BeforeValidator,
    field_validator,
)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):

    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str = "Context QA"

    SECRET_KEY_ACCESS_API: str

    @field_validator("SECRET_KEY_ACCESS_API")
    @classmethod
    def _secret_key_long_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY_ACCESS_API must be at least 32 characters; "
                'generate one with: python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return v

    # Comma-separated list or JSON list of allowed browser origins.
    BACKEND_CORS_ORIGINS: Annotated[list[str] | str, BeforeValidator(parse_cors)] = [
        "http://localhost:3000"
    ]

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_PASS: str
    DB_USER: str

    OPENAI_API_KEY: str
    OPENAI_ORGANIZATION: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_DATABASE_URI(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = "../.env"


class LogConfig:
    LOGGING_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOGGING_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"

    @staticmethod
    def configure_logging():
        logger.remove()

        logger.add(
            sys.stderr, format=LogConfig.LOGGING_FORMAT, level=LogConfig.LOGGING_LEVEL
        )


LogConfig.configure_logging()

settings = Settings()
