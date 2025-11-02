"""
Сервис планировщика задач (APScheduler)
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.date import DateTrigger

from bot.config import Config
from bot.database import engine

logger = logging.getLogger(__name__)


class SchedulerService:
    """Сервис для управления планировщиком задач"""
    
    def __init__(self):
        # Хранилище задач в БД для персистентности
        jobstore = SQLAlchemyJobStore(engine=engine)
        
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': jobstore},
            executors={'default': ThreadPoolExecutor(20)},
            job_defaults={'coalesce': True, 'max_instances': 3},
            timezone=Config.SCHEDULER_TIMEZONE
        )
    
    def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        logger.info("Планировщик задач запущен")
    
    def shutdown(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик задач остановлен")
    
    def schedule_reminder(self, appointment_id: int, appointment_date: datetime, callback_func, bot=None):
        """
        Планирование напоминания за 24 часа до записи
        
        Args:
            appointment_id: ID записи
            appointment_date: Дата и время записи
            callback_func: Функция для вызова при срабатывании
            bot: Экземпляр бота (опционально)
        """
        reminder_time = appointment_date - timedelta(hours=24)
        
        # Не планируем, если время уже прошло
        if reminder_time < datetime.now():
            logger.warning(f"Время напоминания уже прошло для записи {appointment_id}")
            return
        
        job_id = f"reminder_{appointment_id}"
        kwargs = {'bot': bot} if bot else {}
        self.scheduler.add_job(
            callback_func,
            trigger=DateTrigger(run_date=reminder_time),
            id=job_id,
            args=[appointment_id],
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Запланировано напоминание для записи {appointment_id} на {reminder_time}")
    
    def schedule_survey(self, appointment_id: int, appointment_date: datetime, callback_func, bot=None):
        """
        Планирование опроса через 3 дня после процедуры
        
        Args:
            appointment_id: ID записи
            appointment_date: Дата и время записи
            callback_func: Функция для вызова при срабатывании
            bot: Экземпляр бота (опционально)
        """
        survey_time = appointment_date + timedelta(days=3)
        
        job_id = f"survey_{appointment_id}"
        kwargs = {'bot': bot} if bot else {}
        self.scheduler.add_job(
            callback_func,
            trigger=DateTrigger(run_date=survey_time),
            id=job_id,
            args=[appointment_id],
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Запланирован опрос для записи {appointment_id} на {survey_time}")
    
    def cancel_job(self, job_id: str):
        """Отмена задачи"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Задача {job_id} отменена")
        except Exception as e:
            logger.error(f"Ошибка отмены задачи {job_id}: {e}")

