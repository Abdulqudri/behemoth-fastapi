from datetime import date
from typing import Optional

from pydantic import BaseModel, Field



class EventCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    date: date
    location: str = Field(min_length=1, max_length=200)


