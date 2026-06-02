import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str
    host: str
    port: int
    debug: bool
    database_url: str
    jwt_secret_key: str
    webhook_secret_key: str


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "payment-ledger-api"),
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "8000")),
        debug=_get_bool("APP_DEBUG", True),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/payment_ledger",
        ),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-me"),
        webhook_secret_key=os.getenv("WEBHOOK_SECRET_KEY", "change-me"),
    )


settings = load_settings()
