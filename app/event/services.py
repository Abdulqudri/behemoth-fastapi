# app/event/services.py
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import Forbidden, NotFound
from app.common.paginators import paginate, get_pagination_metadata
from app.common.schemas import ResponseSchema
from app.user.models import User, Role
from app.common.types import PaginationParamsType
from app.user.crud import UserCRUD
from app.event.crud import EventCRUD
from app.event.models import Event, EventStatus

from app.event.schemas.create import EventCreateRequest
from app.event.schemas.edit import EventUpdateRequest, EventStatusUpdateRequest
from app.event.schemas.response import EventOut, EventListResponse, EventResponse


class EventService:
    @staticmethod
    def _base_filters(
        *,
        q: Optional[str],
        status: Optional[EventStatus],
        date_from: Optional[date],
        date_to: Optional[date],
    ):
        filters = []
        if q:
            filters.append(Event.title.ilike(f"%{q}%"))
        if status:
            filters.append(Event.status == status)
        if date_from and date_to:
            filters.append(and_(Event.date >= date_from, Event.date <= date_to))
        elif date_from:
            filters.append(Event.date >= date_from)
        elif date_to:
            filters.append(Event.date <= date_to)
        return filters

    # ---------- Create ----------
    @staticmethod
    async def create_event(
        *,
        payload: EventCreateRequest,
        session: AsyncSession,
        current_user: User,
        owner_id_override: Optional[int] = None,  # admin may create for someone else
    ) -> EventResponse:
        event_crud = EventCRUD(Event, session)

        owner_id = current_user.id
        if owner_id_override is not None:
            if current_user.role != Role.ADMIN:
                raise Forbidden(msg="Only admin can create events for other users")
            # Validate target owner exists
            user_crud = UserCRUD(User, session)
            target_owner = await user_crud.get(id=owner_id_override)
            if not target_owner:
                raise NotFound(msg="Target owner not found")
            owner_id = owner_id_override

        event = await event_crud.create_for_owner(
            owner_id=owner_id,
            data={
                "title": payload.title,
                "description": payload.description,
                "date": payload.date,
                "location": payload.location,
                "status": EventStatus.UPCOMING,
            },
        )

        return EventResponse(
            msg="Event created successfully",
            data=EventOut.from_orm_model(event),
        )

    # ---------- Get one ----------
    @staticmethod
    async def get_event(
        *,
        event_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> EventResponse:
        stmt = (
            select(Event)
            .options(
                selectinload(Event.owner),
                selectinload(Event.tasks),
            )
            .where(Event.id == event_id)
        )
        result = await session.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise NotFound(msg="Event not found")

        if current_user.role != Role.ADMIN and event.owner_id != current_user.id:
            raise Forbidden(msg="You do not have access to this event")

        return EventResponse(
            msg="Event fetched successfully",
            data=EventOut.from_orm_model(event),
        )

    # ---------- List (me) ----------
    @staticmethod
    async def list_my_events(
        *,
        session: AsyncSession,
        current_user: User,
        params: PaginationParamsType,
        status: Optional[EventStatus],
        date_from: Optional[date],
        date_to: Optional[date],
    ) -> EventListResponse:
        filters = [Event.owner_id == current_user.id]
        filters += EventService._base_filters(
            q=params.q, status=status, date_from=date_from, date_to=date_to
        )

        # count
        total_q = select(func.count()).select_from(Event).where(*filters)
        total = (await session.execute(total_q)).scalar() or 0

        # base query
        qs = (
            select(Event)
            .options(
                selectinload(Event.owner),
                selectinload(Event.tasks),
            )
            .where(*filters)
            .order_by(Event.id.desc() if params.order_by == "desc" else Event.id.asc())
        )

        # paginate
        paginated_qs = await paginate(qs=qs, page=params.page, size=params.size)
        rows = (await session.execute(paginated_qs)).scalars().all()

        meta = await get_pagination_metadata(
            tno_items=total,
            count=len(rows),
            page=params.page,
            size=params.size,
        )
        return EventListResponse(
            msg="Events fetched successfully",
            data=[EventOut.from_orm_model(e) for e in rows],
            meta=meta,
        )

    # ---------- List (admin) ----------
    @staticmethod
    async def list_all_events_admin(
        *,
        session: AsyncSession,
        params: PaginationParamsType,
        status: Optional[EventStatus],
        date_from: Optional[date],
        date_to: Optional[date],
    ) -> EventListResponse:
        filters = EventService._base_filters(
            q=params.q, status=status, date_from=date_from, date_to=date_to
        )

        total_q = select(func.count()).select_from(Event).where(*filters)
        total = (await session.execute(total_q)).scalar() or 0

        qs = (
            select(Event)
            .options(
                selectinload(Event.owner),
                selectinload(Event.tasks),
            )
            .where(*filters)
            .order_by(Event.id.desc() if params.order_by == "desc" else Event.id.asc())
        )

        paginated_qs = await paginate(qs=qs, page=params.page, size=params.size)
        rows = (await session.execute(paginated_qs)).scalars().all()

        meta = await get_pagination_metadata(
            tno_items=total,
            count=len(rows),
            page=params.page,
            size=params.size,
        )
        return EventListResponse(
            msg="Events fetched successfully",
            data=[EventOut.from_orm_model(e) for e in rows],
            meta=meta,
        )

    # ---------- Update (owner/admin) ----------
    @staticmethod
    async def update_event(
        *,
        event_id: int,
        payload: EventUpdateRequest,
        session: AsyncSession,
        current_user: User,
    ) -> EventResponse:
        stmt = (
            select(Event)
            .options(
                selectinload(Event.owner),
                selectinload(Event.tasks),
            )
            .where(Event.id == event_id)
        )
        result = await session.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise NotFound(msg="Event not found")

        if current_user.role != Role.ADMIN and event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot modify this event")

        update_data = payload.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(event, k, v)

        await session.commit()
        await session.refresh(event)
        return EventResponse(
            msg="Event updated successfully",
            data=EventOut.from_orm_model(event),
        )

    # ---------- Update Status (admin only) ----------
    @staticmethod
    async def update_event_status_admin(
        *,
        event_id: int,
        payload: EventStatusUpdateRequest,
        session: AsyncSession,
        current_user: User,
    ) -> EventResponse:
        if current_user.role != Role.ADMIN:
            raise Forbidden(msg="Only admin can update event status")

        stmt = (
            select(Event)
            .options(
                selectinload(Event.owner),
                selectinload(Event.tasks),
            )
            .where(Event.id == event_id)
        )
        result = await session.execute(stmt)
        event = result.scalar_one_or_none()

        if not event:
            raise NotFound(msg="Event not found")

        event.status = payload.status
        await session.commit()
        await session.refresh(event)
        return EventResponse(
            msg="Event status updated successfully",
            data=EventOut.from_orm_model(event),
        )

    # ---------- Delete ----------
    @staticmethod
    async def delete_event(
        *,
        event_id: int,
        session: AsyncSession,
        current_user: User,
    ) -> ResponseSchema:
        event = await session.get(Event, event_id)
        if not event:
            raise NotFound(msg="Event not found")

        if current_user.role != Role.ADMIN and event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot delete this event")

        await session.delete(event)
        await session.commit()
        return ResponseSchema(msg="Event deleted successfully", data=None)
