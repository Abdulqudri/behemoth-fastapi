# app/task/crud.py
from app.common.crud import CRUDBase
from app.task.models import Task  # ensure this path matches your project


class TaskCRUD(CRUDBase[Task]):
    """Task-specific CRUD helpers (extends generic CRUDBase)."""
    # You can add task-specific helpers here later
    pass
