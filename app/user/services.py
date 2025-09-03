from app.common.exceptions import NotFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.user.models import User
from app.user.schemas.base import UserOut 
from app.user.schemas.edit import UpdateUserRequest
from app.common.paginators import paginate, get_pagination_metadata
from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.user.crud import UserCRUD


class AdminUserService:

    @staticmethod
    async def get_all_users(session: AsyncSession, page: int, size: int) -> PaginatedResponseSchema:
        # Count total users
        total_query = await session.execute(select(func.count()).select_from(User))
        total = total_query.scalar() or 0

        # Paginate query
        user_crud = UserCRUD(User, session)
        qs = await user_crud.get_all(return_qs=True)
        qs = qs.order_by(User.id)
        paginated_qs = await paginate(qs=qs, page=page, size=size)

        result = await session.execute(paginated_qs)
        users = result.scalars().all()

        meta = await get_pagination_metadata(
            tno_items=total,
            count=len(users),
            page=page,
            size=size,
        )

        return PaginatedResponseSchema(
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

        await session.delete(user)
        await session.commit()

        return ResponseSchema(msg="User deleted successfully", data=None)
    
    
    # use to deactivate users 
    @staticmethod
    async def update_user(user_id: int, data: UpdateUserRequest, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)
        user = await user_crud.get(id=user_id)
        if not user:
            raise NotFound(msg="User not found")

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)

        return ResponseSchema(
            msg="User updated successfully",
            data=UserOut.model_validate(user),
        )
