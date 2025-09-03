from functools import lru_cache
from pydantic import BaseModel


class RouteTags(BaseModel):
    """
    Route tags for API grouping in Swagger docs
    """

    # Core Modules
    auth: str = "Auths"
    user: str = "Users"
    event: str = "Events"
    task: str = "Tasks"


@lru_cache
def get_tags() -> RouteTags:
    """
    Get app route tags (cached)
    """
    return RouteTags()
