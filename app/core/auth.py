from typing import Any

from jwt import ExpiredSignatureError, InvalidTokenError
from sanic import Request
from sanic.response import HTTPResponse, json

from app.core.security import decode_access_token


def get_bearer_token(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    prefix = "Bearer "

    if not header.startswith(prefix):
        return None

    token = header.removeprefix(prefix).strip()
    return token or None


def decode_request_token(
    request: Request,
) -> tuple[dict[str, Any] | None, HTTPResponse | None]:
    token = get_bearer_token(request)

    if token is None:
        return None, json({"error": "Authorization token is required"}, status=401)

    try:
        return decode_access_token(token), None
    except ExpiredSignatureError:
        return None, json({"error": "Token has expired"}, status=401)
    except InvalidTokenError:
        return None, json({"error": "Invalid authorization token"}, status=401)


def require_role(request: Request, role: str) -> tuple[int | None, HTTPResponse | None]:
    payload, error_response = decode_request_token(request)

    if error_response is not None or payload is None:
        return None, error_response

    if payload.get("role") != role:
        return None, json({"error": "Forbidden"}, status=403)

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject.isdigit():
        return None, json({"error": "Invalid authorization token"}, status=401)

    return int(subject), None
