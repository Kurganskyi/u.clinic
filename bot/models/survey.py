"""
Модель опроса клиента
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.database import Base


class Survey(Base):
    """Модель опроса удовлетворенности"""
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Результаты опроса
    rating = Column(Integer, nullable=True)  # 1-5
    sent_at = Column(DateTime, nullable=False)
    answered_at = Column(DateTime, nullable=True)
    yandex_link_sent = Column(Boolean, default=False)  # Была ли отправлена ссылка на Яндекс
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", back_populates="surveys")
    appointment = relationship("Appointment", back_populates="survey")

