from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from database import AsyncSessionLocal
from models.task import Task
from utils import define_quadrant, calculate_urgency


async def update_task_urgency():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск обновления квадрантов...")

    async with AsyncSessionLocal() as db:
        try:
            # Получение активных задач
            result = await db.execute(
                select(Task).where(Task.completed == False)
            )
            tasks = result.scalars().all()

            updated_count = 0

            for task in tasks:
                # Вычисление срочности
                is_urgent = calculate_urgency(task.deadline_at)

                # Вычисление нового квадранта
                new_quadrant = define_quadrant(task.is_important, is_urgent)

                # Обновление в бд квадранта
                if task.quadrant != new_quadrant:
                    task.quadrant = new_quadrant
                    updated_count += 1

            if updated_count > 0:
                await db.commit()
                print(f"Обновлено квадрантов: {updated_count}")
            else:
                print("Нет изменений.")

        except Exception as e:
            print(f"Ошибка при обновлении: {e}")
            await db.rollback()


def start_scheduler():
    scheduler = AsyncIOScheduler()

    # Основная задача: запускаем каждый день в 09:00
    scheduler.add_job(
        update_task_urgency,
        trigger='cron',
        hour=9,
        minute=0,
        id='update_urgency',
        name='Обновление срочности задач',
        replace_existing=True
    )

    # Для тестирования: запуск каждые 5 минут
    scheduler.add_job(
         update_task_urgency,
         trigger='interval',
         minutes=1,
         id='update_urgency_test',
         name='Тестовое обновление срочности',
         replace_existing=True
     )

    scheduler.start()
    print("Планировщик задач запущен")

    return scheduler
