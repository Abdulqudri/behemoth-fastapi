from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query

from app.common.dependencies import get_session, get_current_active_user, get_admin_user
from app.common.annotations import DatabaseSession, PaginationParams

from app.task.schemas.create import TaskCreateRequest
from app.task.schemas.edit import TaskUpdateRequest
from app.task.schemas.response import TaskListResponse, TaskResponse
from app.task.services import TaskService
from app.user.models import User

router = APIRouter()



@router.post("/event/{event_id}", response_model=TaskResponse)
async def create_task_for_event(
    session: DatabaseSession,
    event_id: int = Path(..., gt=0),
    payload: TaskCreateRequest = ...,
    current_user: User = Depends(get_current_active_user),
):
    return await TaskService.create_task(
        event_id=event_id,
        payload=payload,
        session=session,
        current_user=current_user,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    session: DatabaseSession,
    task_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
):
    return await TaskService.get_task(
        task_id=task_id,
        session=session,
        current_user=current_user,
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    session: DatabaseSession,
    task_id: int = Path(..., gt=0),
    payload: TaskUpdateRequest = ...,
    current_user: User = Depends(get_current_active_user),
):
    return await TaskService.update_task(
        task_id=task_id,
        payload=payload,
        session=session,
        current_user=current_user,
    )


@router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(
    session: DatabaseSession,
    task_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
):
    return await TaskService.delete_task(
        task_id=task_id,
        session=session,
        current_user=current_user,
    )
