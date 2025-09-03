from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas.signup import SignupRequest
from app.auth.schemas.login import LoginRequest
from app.auth.services import AuthService
from app.common.dependencies import get_session
from app.common.schemas import ResponseSchema


router = APIRouter()


@router.post("/signup", response_model=ResponseSchema)
async def signup(data: SignupRequest, session: AsyncSession = Depends(get_session)):
    return await AuthService.signup(email=data.email, password=data.password, session=session)


@router.post("/login", response_model=ResponseSchema)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    return await AuthService.login(email=data.email, password=data.password, session=session)

@router.post("/admin", response_model=ResponseSchema, tags=["Admin"])
async def bootstrap_admin(
    data: SignupRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AuthService.bootstrap_admin(
        email=data.email,
        password=data.password,
        session=session
    )