from datetime import datetime

from pydantic import BaseModel, ConfigDict
from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.event.models import EventStatus
from app.task.schemas.response import TaskOut
from typing import List


class EventOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    date: datetime
    location: str
    status: EventStatus
    owner_id: int
    tasks: List[TaskOut] = []

    model_config = ConfigDict(
        from_attributes=True
    )  # 👈 tells Pydantic to accept ORM objects

    @classmethod
    def from_orm_model(cls, obj):
        return cls.model_validate(obj)  # now this works


class EventResponse(ResponseSchema):
    data: EventOut | None = None


class EventListResponse(PaginatedResponseSchema):
    data: list[EventOut]
