from app.common.exceptions import NotFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.user.models import User, Role
from app.user.schemas.base import UserOut 
from app.user.schemas.edit import UpdateUserRequest
from app.common.paginators import paginate, get_pagination_metadata
from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.user.crud import UserCRUD


class AdminUserService:

    @staticmethod
    async def get_all_users(session: AsyncSession, page: int, size: int) -> PaginatedResponseSchema:
        # Count total non-admin users
        total_query = await session.execute(
            select(func.count()).select_from(User).where(User.role != Role.ADMIN)
        )
        total = total_query.scalar() or 0

        # Paginate query excluding admins
        user_crud = UserCRUD(User, session)
        qs = await user_crud.get_all(return_qs=True)
        qs = qs.where(User.role != Role.ADMIN).order_by(User.id)

        paginated_qs = await paginate(qs=qs, page=page, size=size)

        result = await session.execute(paginated_qs)
        users = result.scalars().all()

        # Pagination metadata
        meta = await get_pagination_metadata(
            tno_items=total,
            count=len(users),
            page=page,
            size=size,
        )

        return PaginatedResponseSchema(
            msg="Users fetched successfully",
            data=[UserOut.model_validate(u) for u in users],
            meta=meta,
        )
    @staticmethod
    async def get_user(user_id: int, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)
        user = await user_crud.get(id=user_id)
        if not user:
            raise NotFound(
                msg="User not found",
            )

        return ResponseSchema(
            msg="User fetched successfully",
            data=UserOut.model_validate(user),
        )
        
    @staticmethod
    async def delete_user(user_id: int, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)
        user = await user_crud.get(id=user_id)
        if not user:
            raise NotFound(msg="User not found")

        await user_crud.delete(user)

        return ResponseSchema(
            msg="User deleted successfully",
            data={"id": user.id, "email": user.email},
        )

    @staticmethod
    async def update_user(user_id: int, data: UpdateUserRequest, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)
        user = await user_crud.get(id=user_id)
        if not user:
            raise NotFound(msg="User not found")

        updated_user = await user_crud.update(
            user,
            data.dict(exclude_unset=True)
        )

        return ResponseSchema(
            msg="User updated successfully",
            data=UserOut.model_validate(updated_user),
        )
