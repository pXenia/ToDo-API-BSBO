from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from database import init_db, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from routers import tasks, stats, auth, admin
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск приложения...")
    print("Инициализация базы данных...")
    await init_db()
    print("База данных инициализирована")

    # Запуск планировщика
    scheduler=start_scheduler()
    print("Приложение готово к работе!")
    yield

    print("Остановка планирвщика...")
    scheduler.shutdown()
    print("Остановка приложения...")


app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="2.1.0",
    contact={
        "name": "Попова Ксения",
    },
    lifespan=lifespan
)

app.include_router(tasks.router, prefix="/api/v3")
app.include_router(stats.router, prefix="/api/v3")
app.include_router(auth.router, prefix="/api/v3")
app.include_router(admin.router, prefix="/api/v3")


@app.get("/")
async def read_root() -> dict:
    return {
        "message": "Task Manager API - Управление задачами по матрице Эйзенхауэра",
        "version": "3.0.0",
        "database": "PostgreSQL (Supabase)",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_async_session)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "healthy",
        "database": db_status
    }
