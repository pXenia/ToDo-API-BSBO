# Главный файл приложения
from fastapi import FastAPI, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime

from pyexpat.errors import messages

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Попова Ксения Александровна"
    }
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]

@app.get("/")
async def welcome() -> dict:
    return {"message": "Привет, студент!",
            "api_title": app.title,
            "api_description": app.description,
            "api_version": app.version,
            "api_author": app.contact.get("name"),
    }

@app.get("/tasks/search")
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

@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db), # считает количество записей в хранилище
        "tasks": tasks_db # выводит всё, чта есть в хранилище
    }

@app.get("/tasks/quadrant/{quadrant}")
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

@app.get("/tasks/status")
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

@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )

@app.get("/tasks/status/{status}")
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
