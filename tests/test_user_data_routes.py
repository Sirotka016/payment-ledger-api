from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from app.core.security import create_access_token
from app.main import create_app
from app.routes import users as users_module


@dataclass
class FakeAccount:
    id: int
    balance: Decimal


@dataclass
class FakePayment:
    id: int
    transaction_id: str
    account_id: int
    amount: Decimal
    created_at: datetime


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_accounts_returns_current_user_accounts(monkeypatch):
    async def fake_list_accounts_by_user_id(session, user_id):
        assert user_id == 1
        return [FakeAccount(id=1, balance=Decimal("100.50"))]

    monkeypatch.setattr(
        users_module,
        "list_accounts_by_user_id",
        fake_list_accounts_by_user_id,
    )

    app = create_app("user-accounts-test")
    token = create_access_token(subject="1", role="user")
    _, response = app.test_client.get(
        "/users/me/accounts",
        headers=auth_headers(token),
    )

    assert response.status == 200
    assert response.json == {"accounts": [{"id": 1, "balance": "100.50"}]}


def test_user_payments_returns_current_user_payments(monkeypatch):
    created_at = datetime(2026, 6, 4, 12, 0, tzinfo=UTC)

    async def fake_list_payments_by_user_id(session, user_id):
        assert user_id == 1
        return [
            FakePayment(
                id=1,
                transaction_id="external-transaction-id",
                account_id=1,
                amount=Decimal("25.00"),
                created_at=created_at,
            )
        ]

    monkeypatch.setattr(
        users_module,
        "list_payments_by_user_id",
        fake_list_payments_by_user_id,
    )

    app = create_app("user-payments-test")
    token = create_access_token(subject="1", role="user")
    _, response = app.test_client.get(
        "/users/me/payments",
        headers=auth_headers(token),
    )

    assert response.status == 200
    assert response.json == {
        "payments": [
            {
                "id": 1,
                "transaction_id": "external-transaction-id",
                "account_id": 1,
                "amount": "25.00",
                "created_at": "2026-06-04T12:00:00+00:00",
            }
        ]
    }


def test_admin_token_cannot_access_user_accounts():
    app = create_app("user-accounts-forbidden-test")
    token = create_access_token(subject="1", role="admin")
    _, response = app.test_client.get(
        "/users/me/accounts",
        headers=auth_headers(token),
    )

    assert response.status == 403
    assert response.json == {"error": "Forbidden"}
