import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import create_user, get_user_by_email, get_user_by_username
from core.security import hash_password, verify_hashed_password


PASSWORD_PATTERN = re.compile(r"^[A-Za-z0-9@$!%*?&._-]+$")
EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)


def validate_register_input(
    display_name: str,
    username: str,
    password: str,
    email: str,
) -> None:
    if not display_name.strip():
        raise ValueError("display_name must not be empty")
    if not username.strip():
        raise ValueError("username must not be empty")
    if len(password) < 8:
        raise ValueError("password must be at least 8 characters")
    if not PASSWORD_PATTERN.fullmatch(password):
        raise ValueError("password contains invalid characters")
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("email is invalid")


async def register_user(
    db: AsyncSession,
    display_name: str,
    username: str,
    password: str,
    email: str,
) -> User:
    validate_register_input(
        display_name=display_name,
        username=username,
        password=password,
        email=email,
    )

    return await create_user(
        db=db,
        display_name=display_name,
        username=username,
        password=hash_password(password),
        email=email,
    )



async def login_by_email(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_hashed_password(hash_password(password), user.password):
        return None

    return user
