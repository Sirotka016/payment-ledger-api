from app.config import load_settings


def test_load_settings_uses_environment_values(monkeypatch):
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_HOST", "0.0.0.0")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-test-secret-with-at-least-32-bytes")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("WEBHOOK_SECRET_KEY", "webhook-test-secret")

    settings = load_settings()

    assert settings.app_name == "test-app"
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.debug is False
    assert settings.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert settings.jwt_secret_key == "jwt-test-secret-with-at-least-32-bytes"
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_access_token_expire_minutes == 30
    assert settings.webhook_secret_key == "webhook-test-secret"
