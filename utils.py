from datetime import datetime, timezone
from typing import Optional
from models.task import Task
from schemas import TaskResponse


def calculate_urgency(deadline: Optional[datetime]) -> bool:
    if not deadline:
        return False
    now = datetime.now(timezone.utc)
    delta = (deadline - now).days
    return delta <= 3


def define_quadrant(is_important: bool, is_urgent: bool) -> str:
    if is_important and is_urgent:
        return "Q1"
    elif is_important and not is_urgent:
        return "Q2"
    elif not is_important and is_urgent:
        return "Q3"
    else:
        return "Q4"


def prepare_task_to_response(task: Task) -> TaskResponse:
    is_urgent = calculate_urgency(task.deadline_at)
    # количество дней до дедлайна
    days_until = None
    if task.deadline_at:
        now = datetime.now(timezone.utc)
        days_until = (task.deadline_at - now).days

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        deadline_at=task.deadline_at,
        quadrant=task.quadrant,
        completed=task.completed,
        created_at=task.created_at,
        completed_at=task.completed_at,
        is_urgent=is_urgent,
        days_until_deadline=days_until
    )
