from app.config import load_settings


def test_load_settings_uses_environment_values(monkeypatch):
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_HOST", "0.0.0.0")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("JWT_SECRET_KEY", "jwt-test-secret")
    monkeypatch.setenv("WEBHOOK_SECRET_KEY", "webhook-test-secret")

    settings = load_settings()

    assert settings.app_name == "test-app"
    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.debug is False
    assert settings.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert settings.jwt_secret_key == "jwt-test-secret"
    assert settings.webhook_secret_key == "webhook-test-secret"
