from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import get_session, get_admin_user, pagination_params
from app.common.types import PaginationParamsType
from app.user.services import AdminUserService
from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.user.schemas.edit import UpdateUserRequest

router = APIRouter()


@router.get("/", response_model=PaginatedResponseSchema)
async def get_all_users(
    params: PaginationParamsType = Depends(pagination_params),
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(get_admin_user),
):
    return await AdminUserService.get_all_users(session, params.page, params.size)

@router.get("/{user_id}", response_model=ResponseSchema)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(get_admin_user),
):
    return await AdminUserService.get_user(user_id, session)


@router.delete("/{user_id}", response_model=ResponseSchema)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(get_admin_user),
):
    return await AdminUserService.delete_user(user_id, session)


@router.put("/{user_id}", response_model=ResponseSchema)
async def update_user(
    user_id: int,
    data: UpdateUserRequest,
    session: AsyncSession = Depends(get_session),
    _: dict = Depends(get_admin_user),
):
    return await AdminUserService.update_user(user_id, data, session)
