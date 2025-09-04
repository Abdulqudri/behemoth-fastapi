from pydantic import BaseModel, EmailStr
from app.user.models import Role


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    is_active: bool

    class Config:
        from_attributes = True
