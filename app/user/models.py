# app/models.py
from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.core.database import DBBase
import enum

class Role(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(DBBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(Role), default=Role.USER)
    events = relationship("Event", back_populates="owner")
