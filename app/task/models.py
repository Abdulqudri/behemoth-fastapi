# app/models.py
from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import DBBase



class Task(DBBase):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="tasks")