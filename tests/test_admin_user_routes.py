from dataclasses import dataclass, field
from decimal import Decimal

from app.core.security import create_access_token, verify_password
from app.main import create_app
from app.routes import admins as admins_module


@dataclass
class FakeAccount:
    id: int
    balance: Decimal


@dataclass
class FakeUser:
    id: int
    email: str
    full_name: str
    password_hash: str = "password-hash"
    accounts: list[FakeAccount] = field(default_factory=list)


class FakeSession:
    def __init__(self):
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.committed = True

    async def refresh(self, instance):
        return None


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def admin_token() -> str:
    return create_access_token(subject="1", role="admin")


def test_admin_users_returns_users_with_accounts(monkeypatch):
    async def fake_list_users_with_accounts(session):
        return [
            FakeUser(
                id=1,
                email="user@example.com",
                full_name="Test User",
                accounts=[FakeAccount(id=1, balance=Decimal("0.00"))],
            )
        ]

    monkeypatch.setattr(
        admins_module,
        "list_users_with_accounts",
        fake_list_users_with_accounts,
    )

    app = create_app("admin-users-list-test")
    _, response = app.test_client.get(
        "/admins/users",
        headers=auth_headers(admin_token()),
    )

    assert response.status == 200
    assert response.json == {
        "users": [
            {
                "id": 1,
                "email": "user@example.com",
                "full_name": "Test User",
                "accounts": [{"id": 1, "balance": "0.00"}],
            }
        ]
    }


def test_admin_can_create_user(monkeypatch):
    async def fake_get_user_by_email(session, email):
        return None

    async def fake_create_user(session, email, password_hash, full_name):
        assert email == "new@example.com"
        assert verify_password("new-password", password_hash) is True
        return FakeUser(id=2, email=email, full_name=full_name)

    monkeypatch.setattr(admins_module, "SessionLocal", FakeSession)
    monkeypatch.setattr(admins_module, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(admins_module, "create_user", fake_create_user)

    app = create_app("admin-create-user-test")
    _, response = app.test_client.post(
        "/admins/users",
        headers=auth_headers(admin_token()),
        json={
            "email": "new@example.com",
            "password": "new-password",
            "full_name": "New User",
        },
    )

    assert response.status == 201
    assert response.json == {
        "id": 2,
        "email": "new@example.com",
        "full_name": "New User",
    }


def test_admin_create_user_rejects_duplicate_email(monkeypatch):
    async def fake_get_user_by_email(session, email):
        return FakeUser(id=2, email=email, full_name="Existing User")

    monkeypatch.setattr(admins_module, "get_user_by_email", fake_get_user_by_email)

    app = create_app("admin-create-user-duplicate-test")
    _, response = app.test_client.post(
        "/admins/users",
        headers=auth_headers(admin_token()),
        json={
            "email": "existing@example.com",
            "password": "new-password",
            "full_name": "New User",
        },
    )

    assert response.status == 409
    assert response.json == {"error": "User with this email already exists"}


def test_admin_can_update_user(monkeypatch):
    user = FakeUser(id=2, email="old@example.com", full_name="Old Name")

    async def fake_get_user_by_id(session, user_id):
        assert user_id == 2
        return user

    async def fake_get_user_by_email(session, email):
        return None

    monkeypatch.setattr(admins_module, "SessionLocal", FakeSession)
    monkeypatch.setattr(admins_module, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(admins_module, "get_user_by_email", fake_get_user_by_email)

    app = create_app("admin-update-user-test")
    _, response = app.test_client.patch(
        "/admins/users/2",
        headers=auth_headers(admin_token()),
        json={
            "email": "updated@example.com",
            "full_name": "Updated Name",
            "password": "updated-password",
        },
    )

    assert response.status == 200
    assert response.json == {
        "id": 2,
        "email": "updated@example.com",
        "full_name": "Updated Name",
    }
    assert verify_password("updated-password", user.password_hash) is True


def test_admin_can_delete_user(monkeypatch):
    deleted_users = []
    user = FakeUser(id=2, email="user@example.com", full_name="Test User")

    async def fake_get_user_by_id(session, user_id):
        assert user_id == 2
        return user

    async def fake_delete_user(session, user_to_delete):
        deleted_users.append(user_to_delete.id)

    monkeypatch.setattr(admins_module, "SessionLocal", FakeSession)
    monkeypatch.setattr(admins_module, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(admins_module, "delete_user", fake_delete_user)

    app = create_app("admin-delete-user-test")
    _, response = app.test_client.delete(
        "/admins/users/2",
        headers=auth_headers(admin_token()),
    )

    assert response.status == 200
    assert response.json == {"status": "deleted"}
    assert deleted_users == [2]


def test_user_token_cannot_manage_users():
    app = create_app("admin-users-forbidden-test")
    token = create_access_token(subject="1", role="user")
    _, response = app.test_client.get(
        "/admins/users",
        headers=auth_headers(token),
    )

    assert response.status == 403
    assert response.json == {"error": "Forbidden"}
