"""
Инициализация и настройка базы данных
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bot.config import Config

logger = logging.getLogger(__name__)

# Создание движка БД
engine = create_engine(
    Config.DATABASE_URL,
    echo=Config.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {}
)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Получение сессии БД (dependency injection)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация БД (создание таблиц)"""
    from bot.models import User, Appointment, Survey, InteractionLog  # noqa: F401
    
    logger.info("Создание таблиц в БД...")
    Base.metadata.create_all(bind=engine)
    logger.info("Таблицы созданы")

