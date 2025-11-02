"""
Модель пользователя Telegram
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.database import Base


class User(Base):
    """Модель пользователя Telegram"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True, index=True)
    phone_hash = Column(String, nullable=True, index=True)  # Для персонализированных ссылок
    linked_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    appointments = relationship("Appointment", back_populates="user")
    surveys = relationship("Survey", back_populates="user")

