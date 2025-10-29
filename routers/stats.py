from fastapi import APIRouter, HTTPException
from typing import Dict
from database import tasks_db

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    responses = {404: {"description":"Task not found"}}
)

@router.get("/")
async def get_tasks_stats() -> dict:
    total_tasks = len(tasks_db)
    by_quadrant: Dict[str, int] = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status: Dict[str, int] = {"completed": 0, "pending": 0}

    for task in tasks_db:
        quadrant = task.get("quadrant")
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1

        if task.get("completed"):
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1

    print(by_quadrant)
    print(by_status)

    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }