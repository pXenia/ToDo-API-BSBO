from datetime import datetime, timezone, date
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from models.task import Task
from models import User
from schemas import TimingStatsResponse, TaskResponse
from utils import prepare_task_to_response
from dependencies import get_current_user


router = APIRouter(
 prefix="/stats",
 tags=["statistics"]
)

@router.get("/", response_model=dict)
async def get_tasks_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> dict:
    # Все задачи с учетом роли пользователя
    if current_user.role.value == "admin":
        result = await db.execute(select(Task))
    else:
        result = await db.execute(select(Task).where(Task.user_id == current_user.id))

    tasks = result.scalars().all()

    total_tasks = len(tasks)

    # Подсчет по квадрантам
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1

    # Подсчет по статусу
    by_status = {"completed": 0, "pending": 0}
    for task in tasks:
        if task.completed:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }



@router.get("/deadlines", response_model=list)
async def get_deadline_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    # Все задачи с установленным сроком и не выполненные
    if current_user.role.value == "admin":
        result = await db.execute(
            select(Task).where(Task.completed == False, Task.deadline_at.isnot(None))
        )
    else:
        result = await db.execute(
            select(Task).where(
                Task.completed == False,
                Task.deadline_at.isnot(None),
                Task.user_id == current_user.id
            )
        )

    tasks = result.scalars().all()
    now = datetime.now(timezone.utc)

    stats = []
    for task in tasks:
        days_to_deadline = (task.deadline_at - now).days
        stats.append({
            "title": task.title,
            "description": task.description,
            "created_at": task.created_at,
            "deadline_at": task.deadline_at,
            "days_remaining": days_to_deadline
        })

    # Сортировка по оставшимся дням
    stats.sort(key=lambda x: x["days_remaining"])
    return stats


@router.get("/timing", response_model=TimingStatsResponse)
async def get_timing_stats(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> TimingStatsResponse:
    now_utc = datetime.now(timezone.utc)

    # Все задачи с учетом роли пользователя
    if current_user.role.value == "admin":
        result = await db.execute(select(Task))
    else:
        result = await db.execute(select(Task).where(Task.user_id == current_user.id))

    tasks = result.scalars().all()

    completed_on_time = 0
    completed_late = 0
    on_plan_pending = 0
    overtime_pending = 0

    for task in tasks:
        if task.completed:
            if task.completed_at and task.deadline_at:
                if task.completed_at <= task.deadline_at:
                    completed_on_time += 1
                else:
                    completed_late += 1
        else:
            if task.deadline_at:
                if task.deadline_at > now_utc:
                    on_plan_pending += 1
                else:
                    overtime_pending += 1

    return TimingStatsResponse(
        completed_on_time=completed_on_time,
        completed_late=completed_late,
        on_plan_pending=on_plan_pending,
        overtime_pending=overtime_pending,
    )

@router.get("/today", response_model=list[TaskResponse])
async def get_tasks_for_today(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    # Фильтр по пользователю
    if current_user.role.value == "admin":
        stmt = select(Task).where(
            func.date(Task.deadline_at) == today,
            Task.completed == False
        )
    else:
        stmt = select(Task).where(
            func.date(Task.deadline_at) == today,
            Task.completed == False,
            Task.user_id == current_user.id
        )

    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return [prepare_task_to_response(task) for task in tasks]