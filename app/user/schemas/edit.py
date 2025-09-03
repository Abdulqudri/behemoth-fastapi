from pydantic import BaseModel
from app.user.models import Role

class UpdateUserRequest(BaseModel):
    is_active: bool | None = None
