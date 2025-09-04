# app/task/services.py
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFound, Forbidden, BadRequest
from app.common.paginators import paginate, get_pagination_metadata
from app.common.schemas import ResponseSchema, PaginatedResponseSchema
from app.user.models import User, Role
from app.event.models import Event
from app.task.models import Task
from app.task.schemas.create import TaskCreateRequest
from app.task.schemas.edit import TaskUpdateRequest
from app.task.schemas.response import TaskListResponse, TaskResponse, TaskOut
from app.task.crud import TaskCRUD
from app.user.crud import UserCRUD


class TaskService:
    @staticmethod
    async def create_task(
        *,
        event_id: int,
        payload: TaskCreateRequest,
        session: AsyncSession,
        current_user: User,
    ) -> TaskResponse:
        # validate event exists
        event = await session.get(Event, event_id)
        if not event:
            raise NotFound(msg="Event not found")

        # only owner or admin can create tasks for the event
        if current_user.role != Role.ADMIN and event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot add tasks to this event")

        task_crud = TaskCRUD(Task, session)
        task = await task_crud.create(
            data={
                "title": payload.title,
                "description": payload.description,
                "event_id": event_id,
            }
        )

        return TaskResponse(msg="Task created successfully", data=TaskOut.model_validate(task))

    @staticmethod
    async def get_task(
        *, task_id: int, session: AsyncSession, current_user: User
    ) -> TaskResponse:
        task = await session.get(Task, task_id)
        if not task:
            raise NotFound(msg="Task not found")

        # ensure access
        if current_user.role != Role.ADMIN and task.event.owner_id != current_user.id:
            # note: task.event may be lazy-loaded; ensure we fetched owner_id via relationship in model
            raise Forbidden(msg="You do not have access to this task")

        return TaskResponse(msg="Task fetched successfully", data=TaskOut.model_validate(task))

    @staticmethod
    async def list_tasks_for_event(
        *,
        event_id: int,
        session: AsyncSession,
        page: int,
        size: int,
        current_user: User,
    ) -> TaskListResponse:
        # validate event exists
        event = await session.get(Event, event_id)
        if not event:
            raise NotFound(msg="Event not found")

        if current_user.role != Role.ADMIN and event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot view tasks for this event")

        # total count
        total_q = await session.execute(select(func.count()).select_from(Task).where(Task.event_id == event_id))
        total = total_q.scalar() or 0

        qs = select(Task).where(Task.event_id == event_id).order_by(Task.id.desc())
        paginated_qs = await paginate(qs=qs, page=page, size=size)

        result = await session.execute(paginated_qs)
        items = result.scalars().all()

        meta = await get_pagination_metadata(tno_items=total, count=len(items), page=page, size=size)
        return TaskListResponse(msg="Tasks fetched successfully", data=[TaskOut.model_validate(t) for t in items], meta=meta)

    @staticmethod
    async def update_task(
        *, task_id: int, payload: TaskUpdateRequest, session: AsyncSession, current_user: User
    ) -> TaskResponse:
        task = await session.get(Task, task_id)
        if not task:
            raise NotFound(msg="Task not found")

        if current_user.role != Role.ADMIN and task.event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot modify this task")

        update_data = payload.model_dump(exclude_unset=True)
        task_crud = TaskCRUD(Task, session)
        updated = await task_crud.update(task, update_data)

        return TaskResponse(msg="Task updated successfully", data=TaskOut.model_validate(updated))

    @staticmethod
    async def delete_task(
        *, task_id: int, session: AsyncSession, current_user: User
    ) -> ResponseSchema:
        task = await session.get(Task, task_id)
        if not task:
            raise NotFound(msg="Task not found")

        if current_user.role != Role.ADMIN and task.event.owner_id != current_user.id:
            raise Forbidden(msg="You cannot delete this task")

        task_crud = TaskCRUD(Task, session)
        await task_crud.delete(task)
        return ResponseSchema(msg="Task deleted successfully", data=None)
