from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# --- Pydantic Модели ---

## Базовая схема для Task.
## Содержит все поля, общие для создания и ответа.
class TaskBase(BaseModel):
    title: str = Field(
        ...,  # Обязательное поле
        min_length=3,
        max_length=100,
        description="Название задачи"
    )
    description: Optional[str] = Field(
        None,  # Необязательное поле
        max_length=500,
        description="Описание задачи"
    )
    is_important: bool = Field(
        ...,  # Обязательное поле
        description="Важность задачи"
    )
    deadline_at: Optional[datetime] = Field(
        None,
        description="Плановый дедлайн"
    )

## Схема для создания новой задачи
## Наследует все поля от TaskBase
class TaskCreate(TaskBase):
    pass

## Схема для обновления задачи (используется в PUT/PATCH)
## Все поля опциональные (Optional[...]), т.к. можно обновить только часть полей.
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Новое название задачи"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание"
    )
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность"
    )
    deadline_at: Optional[datetime] = Field(
        None,
        description="Дедлайн"
    )
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения"
    )

## Модель для ответа (TaskResponse)
## Включает сгенерированные поля (id, created_at, quadrant) и наследует TaskBase.
class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор задачи",
        examples=[1]
    )
    quadrant: str = Field(
        ...,
        description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
        examples=["Q1"]
    )
    completed: bool = Field(
        default=False,
        description="Статус выполнения задачи"
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи"
    )
    completed_at: Optional[datetime] = Field(
        ...,
        description="Дата завершения задачи"
    )
    is_urgent: bool = Field(
        ...,
        description="Рассчитанная срочность"
    )
    days_until_deadline: Optional[int] = Field(
        None,
        description="Дней до дедлайна")



    class Config:
        # Config класс для работы с ORM (понадобится после подключения СУБД)
        from_attributes = True