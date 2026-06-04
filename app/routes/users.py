from sanic import Blueprint, Request
from sanic.response import HTTPResponse, json

from app.core.auth import require_role
from app.db import SessionLocal
from app.models import Account, Payment
from app.repositories.accounts import list_accounts_by_user_id
from app.repositories.payments import list_payments_by_user_id
from app.repositories.users import get_user_by_id

users_bp = Blueprint("users", url_prefix="/users")


def serialize_account(account: Account) -> dict[str, object]:
    return {
        "id": account.id,
        "balance": str(account.balance),
    }


def serialize_payment(payment: Payment) -> dict[str, object]:
    return {
        "id": payment.id,
        "transaction_id": payment.transaction_id,
        "account_id": payment.account_id,
        "amount": str(payment.amount),
        "created_at": payment.created_at.isoformat(),
    }


@users_bp.get("/me")
async def get_current_user(request: Request) -> HTTPResponse:
    user_id, error_response = require_role(request, "user")

    if error_response is not None or user_id is None:
        return error_response

    async with SessionLocal() as session:
        user = await get_user_by_id(session, user_id)

    if user is None:
        return json({"error": "User not found"}, status=404)

    return json(
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
        }
    )


@users_bp.get("/me/accounts")
async def get_current_user_accounts(request: Request) -> HTTPResponse:
    user_id, error_response = require_role(request, "user")

    if error_response is not None or user_id is None:
        return error_response

    async with SessionLocal() as session:
        accounts = await list_accounts_by_user_id(session, user_id)

    return json({"accounts": [serialize_account(account) for account in accounts]})


@users_bp.get("/me/payments")
async def get_current_user_payments(request: Request) -> HTTPResponse:
    user_id, error_response = require_role(request, "user")

    if error_response is not None or user_id is None:
        return error_response

    async with SessionLocal() as session:
        payments = await list_payments_by_user_id(session, user_id)

    return json({"payments": [serialize_payment(payment) for payment in payments]})
