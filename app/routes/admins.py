from sanic import Blueprint, Request
from sanic.response import HTTPResponse, json

from app.core.auth import require_role
from app.core.security import hash_password
from app.db import SessionLocal
from app.models import Account, User
from app.repositories.admins import get_admin_by_id
from app.repositories.users import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    list_users_with_accounts,
)
from app.schemas.users import (
    parse_user_create_request,
    parse_user_update_request,
)

admins_bp = Blueprint("admins", url_prefix="/admins")


def serialize_user(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }


def serialize_account(account: Account) -> dict[str, object]:
    return {
        "id": account.id,
        "balance": str(account.balance),
    }


def serialize_user_with_accounts(user: User) -> dict[str, object]:
    data = serialize_user(user)
    data["accounts"] = [serialize_account(account) for account in user.accounts]
    return data


@admins_bp.get("/me")
async def get_current_admin(request: Request) -> HTTPResponse:
    admin_id, error_response = require_role(request, "admin")

    if error_response is not None or admin_id is None:
        return error_response

    async with SessionLocal() as session:
        admin = await get_admin_by_id(session, admin_id)

    if admin is None:
        return json({"error": "Admin not found"}, status=404)

    return json(
        {
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
        }
    )


@admins_bp.get("/users")
async def get_users(request: Request) -> HTTPResponse:
    admin_id, error_response = require_role(request, "admin")

    if error_response is not None or admin_id is None:
        return error_response

    async with SessionLocal() as session:
        users = await list_users_with_accounts(session)

    return json({"users": [serialize_user_with_accounts(user) for user in users]})


@admins_bp.post("/users")
async def create_user_by_admin(request: Request) -> HTTPResponse:
    admin_id, error_response = require_role(request, "admin")

    if error_response is not None or admin_id is None:
        return error_response

    user_data, parse_error = parse_user_create_request(request.json)

    if parse_error is not None or user_data is None:
        return json({"error": parse_error}, status=400)

    async with SessionLocal() as session:
        existing_user = await get_user_by_email(session, user_data.email)

        if existing_user is not None:
            return json({"error": "User with this email already exists"}, status=409)

        user = await create_user(
            session,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        await session.commit()
        await session.refresh(user)

    return json(serialize_user(user), status=201)


@admins_bp.patch("/users/<user_id:int>")
async def update_user_by_admin(request: Request, user_id: int) -> HTTPResponse:
    admin_id, error_response = require_role(request, "admin")

    if error_response is not None or admin_id is None:
        return error_response

    user_data, parse_error = parse_user_update_request(request.json)

    if parse_error is not None or user_data is None:
        return json({"error": parse_error}, status=400)

    async with SessionLocal() as session:
        user = await get_user_by_id(session, user_id)

        if user is None:
            return json({"error": "User not found"}, status=404)

        if user_data.email is not None and user_data.email != user.email:
            existing_user = await get_user_by_email(session, user_data.email)

            if existing_user is not None:
                return json(
                    {"error": "User with this email already exists"}, status=409
                )

            user.email = user_data.email

        if user_data.full_name is not None:
            user.full_name = user_data.full_name

        if user_data.password is not None:
            user.password_hash = hash_password(user_data.password)

        await session.commit()
        await session.refresh(user)

    return json(serialize_user(user))


@admins_bp.delete("/users/<user_id:int>")
async def delete_user_by_admin(request: Request, user_id: int) -> HTTPResponse:
    admin_id, error_response = require_role(request, "admin")

    if error_response is not None or admin_id is None:
        return error_response

    async with SessionLocal() as session:
        user = await get_user_by_id(session, user_id)

        if user is None:
            return json({"error": "User not found"}, status=404)

        await delete_user(session, user)
        await session.commit()

    return json({"status": "deleted"})
