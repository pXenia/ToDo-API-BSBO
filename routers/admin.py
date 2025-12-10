from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_async_session
from dependencies import get_current_admin
from models import User, Task

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.get("/users")
async def get_users_with_task_counts(
    db: AsyncSession = Depends(get_async_session),
    admin: User = Depends(get_current_admin)
):
    stmt = (
        select(
            User.id,
            User.nickname,
            User.email,
            User.role,
            func.count(Task.id).label("tasks_count")
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
    )

    result = await db.execute(stmt)
    users = result.all()

    return [
        {
            "id": u.id,
            "nickname": u.nickname,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else u.role,
            "tasks_count": u.tasks_count
        }
        for u in users
    ]
