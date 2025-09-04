# app/event/routes.py
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends

from app.common.dependencies import (
    get_current_active_user,
    get_admin_user,
)
from app.common.annotations import DatabaseSession, PaginationParams
from app.event.models import EventStatus
from app.event.schemas.create import EventCreateRequest
from app.event.schemas.edit import EventUpdateRequest, EventStatusUpdateRequest
from app.event.schemas.response import EventListResponse, EventResponse
from app.event.services import EventService
from app.user.models import User

router = APIRouter()


# --------- Create ---------
@router.post("", response_model=EventResponse)
async def create_event(
    payload: EventCreateRequest,
    session: DatabaseSession,
    current_user: User = Depends(get_current_active_user),
):
    return await EventService.create_event(
        payload=payload, session=session, current_user=current_user
    )


# (Admin) create event for another user (optional helper)
@router.post("/admin/create-for/{owner_id}", response_model=EventResponse)
async def admin_create_for_user(
    owner_id: int,
    payload: EventCreateRequest,
    session: DatabaseSession,
    admin: User = Depends(get_admin_user),
):
    return await EventService.create_event(
        payload=payload,
        session=session,
        current_user=admin,
        owner_id_override=owner_id,
    )


# --------- List my events ---------
@router.get("", response_model=EventListResponse)
async def list_my_events(
    session: DatabaseSession,
    params: PaginationParams,
    status: Optional[EventStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_active_user),
):
    return await EventService.list_my_events(
        session=session,
        current_user=current_user,
        params=params,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )


# --------- List all (admin) ---------
@router.get("/admin", response_model=EventListResponse)
async def list_all_events_admin(
    session: DatabaseSession,
    params: PaginationParams,
    status: Optional[EventStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    _: User = Depends(get_admin_user),
):
    return await EventService.list_all_events_admin(
        session=session,
        params=params,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )


# --------- Get one ---------
@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    session: DatabaseSession,
    current_user: User = Depends(get_current_active_user),
):
    return await EventService.get_event(
        event_id=event_id, session=session, current_user=current_user
    )


# --------- Update (owner/admin) ---------
@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    payload: EventUpdateRequest,
    session: DatabaseSession,
    current_user: User = Depends(get_current_active_user),
):
    return await EventService.update_event(
        event_id=event_id, payload=payload, session=session, current_user=current_user
    )


# --------- Update status (admin only) ---------
@router.patch("/{event_id}/status", response_model=EventResponse)
async def update_event_status_admin(
    event_id: int,
    payload: EventStatusUpdateRequest,
    session: DatabaseSession,
    admin: User = Depends(get_admin_user),
):
    return await EventService.update_event_status_admin(
        event_id=event_id, payload=payload, session=session, current_user=admin
    )


# --------- Delete ---------
@router.delete("/{event_id}", response_model=EventResponse)
async def delete_event(
    event_id: int,
    session: DatabaseSession,
    current_user: User = Depends(get_current_active_user),
):
    # ResponseSchema fits EventResponse shape (status/msg/data)
    return await EventService.delete_event(
        event_id=event_id, session=session, current_user=current_user
    )
