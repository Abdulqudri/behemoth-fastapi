from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.event.models import Event, EventStatus  # assumes your SQLA model + Enum


class EventUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    date: Optional[date] = None
    location: Optional[str] = Field(default=None, min_length=1, max_length=200)
    # NOTE: regular users cannot update status; admins have a dedicated endpoint


class EventStatusUpdateRequest(BaseModel):
    status: EventStatus