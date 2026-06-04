from dataclasses import dataclass


@dataclass(frozen=True)
class LoginRequest:
    email: str
    password: str


def parse_login_request(data: object) -> tuple[LoginRequest | None, str | None]:
    if not isinstance(data, dict):
        return None, "JSON body is required"

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not email.strip():
        return None, "Email is required"

    if not isinstance(password, str) or not password:
        return None, "Password is required"

    return LoginRequest(email=email.strip().lower(), password=password), None
