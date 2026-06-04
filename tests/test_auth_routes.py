from dataclasses import dataclass

from app.core.security import decode_access_token, hash_password
from app.main import create_app
from app.routes import auth as auth_module


@dataclass
class FakePrincipal:
    id: int
    password_hash: str


def test_user_login_returns_access_token(monkeypatch):
    async def fake_get_user_by_email(session, email):
        assert email == "user@example.com"
        return FakePrincipal(id=1, password_hash=hash_password("user12345"))

    monkeypatch.setattr(auth_module, "get_user_by_email", fake_get_user_by_email)

    app = create_app("user-login-test")
    _, response = app.test_client.post(
        "/auth/user/login",
        json={"email": "user@example.com", "password": "user12345"},
    )

    assert response.status == 200
    assert response.json["token_type"] == "bearer"

    payload = decode_access_token(response.json["access_token"])
    assert payload["sub"] == "1"
    assert payload["role"] == "user"


def test_admin_login_returns_admin_role(monkeypatch):
    async def fake_get_admin_by_email(session, email):
        assert email == "admin@example.com"
        return FakePrincipal(id=1, password_hash=hash_password("admin12345"))

    monkeypatch.setattr(auth_module, "get_admin_by_email", fake_get_admin_by_email)

    app = create_app("admin-login-test")
    _, response = app.test_client.post(
        "/auth/admin/login",
        json={"email": "admin@example.com", "password": "admin12345"},
    )

    assert response.status == 200

    payload = decode_access_token(response.json["access_token"])
    assert payload["sub"] == "1"
    assert payload["role"] == "admin"


def test_login_rejects_wrong_password(monkeypatch):
    async def fake_get_user_by_email(session, email):
        return FakePrincipal(id=1, password_hash=hash_password("user12345"))

    monkeypatch.setattr(auth_module, "get_user_by_email", fake_get_user_by_email)

    app = create_app("wrong-password-test")
    _, response = app.test_client.post(
        "/auth/user/login",
        json={"email": "user@example.com", "password": "wrong"},
    )

    assert response.status == 401
    assert response.json == {"error": "Invalid email or password"}


def test_login_requires_email_and_password():
    app = create_app("login-validation-test")
    _, response = app.test_client.post(
        "/auth/user/login",
        json={"email": "user@example.com"},
    )

    assert response.status == 400
    assert response.json == {"error": "Password is required"}
