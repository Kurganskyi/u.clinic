"""
Модели данных для работы с БД
"""
from bot.models.user import User
from bot.models.appointment import Appointment
from bot.models.survey import Survey
from bot.models.statistics import InteractionLog

__all__ = ["User", "Appointment", "Survey", "InteractionLog"]

