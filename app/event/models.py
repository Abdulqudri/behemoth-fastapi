# app/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import DBBase
import enum


class EventStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Event(DBBase):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    date = Column(DateTime)
    location = Column(String)
    status = Column(Enum(EventStatus), default=EventStatus.UPCOMING)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="events")
    tasks = relationship("Task", back_populates="event", cascade="all, delete-orphan")
