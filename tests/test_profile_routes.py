from dataclasses import dataclass

from app.core.security import create_access_token
from app.main import create_app
from app.routes import admins as admins_module
from app.routes import users as users_module


@dataclass
class FakeProfile:
    id: int
    email: str
    full_name: str


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_me_returns_current_user(monkeypatch):
    async def fake_get_user_by_id(session, user_id):
        assert user_id == 1
        return FakeProfile(
            id=1,
            email="user@example.com",
            full_name="Test User",
        )

    monkeypatch.setattr(users_module, "get_user_by_id", fake_get_user_by_id)

    app = create_app("user-me-test")
    token = create_access_token(subject="1", role="user")
    _, response = app.test_client.get("/users/me", headers=auth_headers(token))

    assert response.status == 200
    assert response.json == {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Test User",
    }


def test_admin_me_returns_current_admin(monkeypatch):
    async def fake_get_admin_by_id(session, admin_id):
        assert admin_id == 1
        return FakeProfile(
            id=1,
            email="admin@example.com",
            full_name="Test Admin",
        )

    monkeypatch.setattr(admins_module, "get_admin_by_id", fake_get_admin_by_id)

    app = create_app("admin-me-test")
    token = create_access_token(subject="1", role="admin")
    _, response = app.test_client.get("/admins/me", headers=auth_headers(token))

    assert response.status == 200
    assert response.json == {
        "id": 1,
        "email": "admin@example.com",
        "full_name": "Test Admin",
    }


def test_profile_requires_token():
    app = create_app("missing-profile-token-test")
    _, response = app.test_client.get("/users/me")

    assert response.status == 401
    assert response.json == {"error": "Authorization token is required"}


def test_user_token_cannot_access_admin_profile():
    app = create_app("profile-forbidden-test")
    token = create_access_token(subject="1", role="user")
    _, response = app.test_client.get("/admins/me", headers=auth_headers(token))

    assert response.status == 403
    assert response.json == {"error": "Forbidden"}


def test_invalid_token_is_rejected():
    app = create_app("invalid-profile-token-test")
    _, response = app.test_client.get(
        "/users/me",
        headers=auth_headers("not-a-real-token"),
    )

    assert response.status == 401
    assert response.json == {"error": "Invalid authorization token"}
