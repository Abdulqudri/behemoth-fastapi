
from app.common.crud import CRUDBase
from app.event.models import Event

class EventCRUD(CRUDBase[Event]):
    """
    Thin wrapper around CRUDBase for Event-specific helpers.
    """

    async def create_for_owner(self, *, owner_id: int, data: dict) -> Event:
        data = {**data, "owner_id": owner_id}
        return await self.create(data=data)
