# app/common/dependencies.py
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.auth import TokenGenerator
from app.common.exceptions import Unauthorized
from app.common.types import PaginationParamsType
from app.core.database import AsyncSessionLocal
from app.core.settings import get_settings
from app.user.models import User, Role

# Globals
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_generator = TokenGenerator(
    secret_key=settings.SECRET_KEY,
    expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)


# Database session
async def get_session() -> AsyncSession:
    """
    Start a db session
    """
    async with AsyncSessionLocal() as session:  # type: ignore
        yield session


# Pagination
def pagination_params(
    q: str | None = None,
    page: int = 1,
    size: int = 10,
    order_by: Literal["asc", "desc"] = "desc",
):
    """
    Helper Dependency for pagination
    """
    return PaginationParamsType(q=q, page=page, size=size, order_by=order_by)


# Auth-related dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Extract current user from JWT token.
    """
    user_id = await token_generator.verify(token=token, sub_head="user")
    if not user_id:
        raise Unauthorized("Invalid authentication token")

    user = await session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the user is active.
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


async def get_admin_user(
    user: User = Depends(get_current_active_user),
) -> User:
    """
    Ensure the user has admin role.
    """
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
