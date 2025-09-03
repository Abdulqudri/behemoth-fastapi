from sqlalchemy.ext.asyncio import AsyncSession
from app.common.exceptions import BadRequest, Unauthorized

from app.user.models import User, Role
from app.common.security import hash_password, verify_password
from app.common.auth import TokenGenerator
from app.core.settings import get_settings
from app.common.schemas import ResponseSchema
from app.user.crud import UserCRUD

settings = get_settings()
token_generator = TokenGenerator(
    secret_key=settings.SECRET_KEY,
    expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
)


from sqlalchemy import select





class AuthService:
    @staticmethod
    async def signup(email: str, password: str, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)

        # Check if user exists
        existing_user = await user_crud.get(email=email)
        if existing_user:
            raise BadRequest(msg="Email already registered")

        # Create new user
        user = await user_crud.create(
            data= {"email": email,
            "hashed_password": await hash_password(raw=password),
            "role": Role.USER}
        )

        return ResponseSchema(
            msg="User created successfully",
            data={"id": user.id, "email": user.email, "role": user.role},
        )

    @staticmethod
    async def login(email: str, password: str, session: AsyncSession) -> ResponseSchema:
        user_crud = UserCRUD(User, session)

        user = await user_crud.get(email=email)
        if not user or not await verify_password(raw=password, hashed=user.hashed_password):
            raise Unauthorized(
                msg="Invalid credentials",
            )

        token = await token_generator.generate(sub=f"user-{user.id}")

        return ResponseSchema(
            msg="Login successful",
            data={"access_token": token, "token_type": "bearer"},
        )