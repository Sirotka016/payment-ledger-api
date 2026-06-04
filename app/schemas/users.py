from dataclasses import dataclass


@dataclass(frozen=True)
class UserCreateRequest:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True)
class UserUpdateRequest:
    email: str | None = None
    password: str | None = None
    full_name: str | None = None


def parse_user_create_request(
    data: object,
) -> tuple[UserCreateRequest | None, str | None]:
    if not isinstance(data, dict):
        return None, "JSON body is required"

    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    if not isinstance(email, str) or not email.strip():
        return None, "Email is required"

    if not isinstance(password, str) or not password:
        return None, "Password is required"

    if not isinstance(full_name, str) or not full_name.strip():
        return None, "Full name is required"

    return (
        UserCreateRequest(
            email=email.strip().lower(),
            password=password,
            full_name=full_name.strip(),
        ),
        None,
    )


def parse_user_update_request(
    data: object,
) -> tuple[UserUpdateRequest | None, str | None]:
    if not isinstance(data, dict):
        return None, "JSON body is required"

    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")

    has_email = "email" in data
    has_password = "password" in data
    has_full_name = "full_name" in data

    if not any([has_email, has_password, has_full_name]):
        return None, "At least one field is required"

    if has_email and (not isinstance(email, str) or not email.strip()):
        return None, "Email must be a non-empty string"

    if has_password and (not isinstance(password, str) or not password):
        return None, "Password must be a non-empty string"

    if has_full_name and (not isinstance(full_name, str) or not full_name.strip()):
        return None, "Full name must be a non-empty string"

    return (
        UserUpdateRequest(
            email=email.strip().lower() if isinstance(email, str) else None,
            password=password if isinstance(password, str) else None,
            full_name=full_name.strip() if isinstance(full_name, str) else None,
        ),
        None,
    )
