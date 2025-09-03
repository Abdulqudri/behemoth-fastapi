from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.event.models import Event, EventStatus


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    date: date
    location: str
    status: EventStatus
    owner_id: int

    @classmethod
    def from_orm_model(cls, obj: Event) -> "EventOut":
        return cls.model_validate(obj)


class EventResponse(ResponseSchema):
    data: EventOut | None = None


class EventListResponse(PaginatedResponseSchema):
    data: list[EventOut]
