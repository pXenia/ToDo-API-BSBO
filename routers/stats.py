from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models.task import Task

router = APIRouter(
 prefix="/stats",
 tags=["statistics"]
)


@router.get("/", response_model=dict)
async def get_tasks_stats(db: AsyncSession = Depends(get_async_session)) -> dict:
    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    total_tasks = len(tasks)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1
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
async def get_deadline_stats(db: AsyncSession = Depends(get_async_session)):
    # Выбор задач из БД со сроком и установленным сроком
    result = await db.execute(
        select(Task).where(Task.completed == False, Task.deadline_at.isnot(None))
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