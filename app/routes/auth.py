from typing import Awaitable, Callable, Protocol

from sanic import Blueprint, Request
from sanic.response import HTTPResponse, json
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.db import SessionLocal
from app.repositories.admins import get_admin_by_email
from app.repositories.users import get_user_by_email
from app.schemas.auth import parse_login_request

auth_bp = Blueprint("auth", url_prefix="/auth")


class Principal(Protocol):
    id: int
    password_hash: str


RepositoryGetter = Callable[[AsyncSession, str], Awaitable[Principal | None]]


async def _login(
    request: Request,
    get_principal_by_email: RepositoryGetter,
    role: str,
) -> HTTPResponse:
    login_data, error = parse_login_request(request.json)

    if error is not None or login_data is None:
        return json({"error": error}, status=400)

    async with SessionLocal() as session:
        principal = await get_principal_by_email(session, login_data.email)

    if principal is None or not verify_password(
        login_data.password,
        principal.password_hash,
    ):
        return json({"error": "Invalid email or password"}, status=401)

    access_token = create_access_token(subject=str(principal.id), role=role)

    return json(
        {
            "access_token": access_token,
            "token_type": "bearer",
        }
    )


@auth_bp.post("/user/login")
async def user_login(request: Request) -> HTTPResponse:
    return await _login(request, get_user_by_email, role="user")


@auth_bp.post("/admin/login")
async def admin_login(request: Request) -> HTTPResponse:
    return await _login(request, get_admin_by_email, role="admin")
