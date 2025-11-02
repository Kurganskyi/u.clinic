"""
Модель для хранения статистики взаимодействий
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from bot.database import Base


class InteractionLog(Base):
    """Лог всех взаимодействий пользователя с ботом"""
    __tablename__ = "interaction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    interaction_type = Column(String, nullable=False, index=True)  # notification, reminder, survey, etc.
    interaction_data = Column(Text, nullable=True)  # JSON данные о взаимодействии
    status = Column(String, nullable=False)  # sent, delivered, read, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

