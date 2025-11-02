"""
Модель записи клиента
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from bot.database import Base


class Appointment(Base):
    """Модель записи клиента"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    bitrix24_deal_id = Column(Integer, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    phone_number = Column(String, nullable=True, index=True)
    
    # Данные о записи
    appointment_date = Column(DateTime, nullable=False)
    procedure_name = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    
    # Статусы
    notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    reminder_confirmed = Column(Boolean, nullable=True)  # True/False/None
    reminder_answered_at = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="appointments")
    survey = relationship("Survey", back_populates="appointment", uselist=False)

