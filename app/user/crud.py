# app/user/crud.py
from app.common.crud import CRUDBase
from app.user.models import User


class UserCRUD(CRUDBase[User]):
    """CRUD operations specific to User"""
    pass
