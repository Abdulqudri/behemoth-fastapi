from typing import Optional, List
from pydantic import BaseModel

from app.common.schemas import ResponseSchema, PaginatedResponseSchema




class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_id: int

    class Config:
        from_attributes = True  # allow building from SQLA objects


class TaskListResponse(PaginatedResponseSchema):
    data: List[TaskOut]


class TaskResponse(ResponseSchema):
    data: Optional[TaskOut] = None
