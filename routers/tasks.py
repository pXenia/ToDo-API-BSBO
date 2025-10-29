from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from starlette import status
from starlette.responses import Response
from database import tasks_db
from schemas import TaskBase, TaskCreate, TaskUpdate, TaskResponse


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses = {404: {"description":"Task not found"}}
)

@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db), # считает количество записей в хранилище
        "tasks": tasks_db # выводит всё, чта есть в хранилище
    }

@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException( #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке
            status_code=400,
                detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4" #текст, который будет выведен пользователю
        )

    filtered_tasks = [
        task # ЧТО добавляем в список
        for task in tasks_db # ОТКУДА берем элементы
        if task["quadrant"] == quadrant # УСЛОВИЕ фильтрации
    ]

    return {
    "quadrant": quadrant,
    "count": len(filtered_tasks),
    "tasks": filtered_tasks
    }

@router.get("/search")
async def search_tasks(
        q: str = Query(..., min_length=2, description="Ключевое слово для поиска в названии или описании")) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос должен содержать минимум 2 символа."
        )

    query_lower = q.lower()

    filtered_tasks = []
    for task in tasks_db:
        title_match = task.get("title", "").lower().find(query_lower) != -1
        description_match = (
                task.get("description", "") is not None and
                task.get("description", "").lower().find(query_lower) != -1
        )

        if title_match or description_match:
            filtered_tasks.append(task)

    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задач по запросу '{q}' не найдено."
        )

    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task(task: TaskCreate) -> TaskResponse:
    if task.is_important and task.is_urgent:
        quadrant = "Q1"  # Важное и Срочное
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"  # Важное, но Не Срочное
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"  # Не Важное, но Срочное
    else:
        quadrant = "Q4"  # Не Важное и Не Срочное

    new_id = max([t["id"] for t in tasks_db], default=0) + 1

    # Создаем новую запись задачи
    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now()
    }

    tasks_db.append(new_task)
    return new_task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    task = next(
        (task for task in tasks_db if task["id"] == task_id),
        None
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    task = next(
        (task for task in tasks_db if task["id"] == task_id),
        None
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        task[field] = value

    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"  # Важное и Срочное
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"  # Важное, но Не Срочное
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"  # Не Важное, но Срочное
        else:
            task["quadrant"] = "Q4"  # Не Важное и Не Срочное

    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = next(
        (task for task in tasks_db if task["id"] == task_id),
        None
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    task["completed"] = True
    task["completed_at"] = datetime.now()
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next(
        (task for task in tasks_db if task["id"] == task_id),
        None
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{status}")
async def get_tasks_by_status(status: str) -> dict:
    status_lower = status.lower()
    if status_lower == "completed":
        is_completed = True
    elif status_lower == "pending":
        is_completed = False
    else:
        raise HTTPException(
            status_code=400,
            detail="Неверный статус. Используйте completed (выполненные) или pending (невыполненные)."
        )

    filtered_tasks = [
        task
        for task in tasks_db
        if task["completed"] == is_completed
    ]

    if not filtered_tasks:
        raise HTTPException(
            status_code=404,
            detail=f"Задач со статусом '{status_lower}' не найдено."
        )

    return {
        "status": status_lower,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }