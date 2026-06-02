from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings
from app.db import SessionLocal, engine


def test_database_engine_uses_settings_url():
    assert isinstance(engine, AsyncEngine)
    assert engine.url.render_as_string(hide_password=False) == settings.database_url


def test_session_factory_is_configured():
    assert SessionLocal.kw["expire_on_commit"] is False
