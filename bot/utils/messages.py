"""
Шаблоны сообщений для бота
"""
from datetime import datetime


def format_appointment_notification(
    appointment_date: datetime,
    doctor_name: str = None,
    procedure_name: str = None,
    address: str = None
) -> str:
    """
    Форматирование уведомления о записи
    
    TODO: Согласовать точный формат с клиентом
    """
    date_str = appointment_date.strftime("%d.%m.%Y")
    time_str = appointment_date.strftime("%H:%M")
    
    message = (
        f"📅 Вы записаны в Uclinic!\n\n"
        f"Дата: {date_str}\n"
        f"Время: {time_str}\n"
    )
    
    if doctor_name:
        message += f"👩‍⚕️ Врач: {doctor_name}\n"
    
    if procedure_name:
        message += f"💆 Процедура: {procedure_name}\n"
    
    if address:
        message += f"\n📍 Адрес: {address}\n"
    
    message += "\nМы напомним вам за 24 часа до визита! ⏰"
    
    return message


def format_reminder_24h(
    appointment_date: datetime,
    doctor_name: str = None,
    procedure_name: str = None
) -> str:
    """Форматирование напоминания за 24 часа"""
    date_str = appointment_date.strftime("%d.%m.%Y")
    time_str = appointment_date.strftime("%H:%M")
    
    message = (
        f"⏰ Напоминание о записи\n\n"
        f"Завтра, {date_str} в {time_str}\n"
    )
    
    if doctor_name:
        message += f"👩‍⚕️ Врач: {doctor_name}\n"
    
    if procedure_name:
        message += f"💆 Процедура: {procedure_name}\n"
    
    message += "\nПожалуйста, подтвердите, что вы придёте:"
    
    return message


def format_survey_message(procedure_name: str = None) -> str:
    """Форматирование сообщения опроса"""
    message = (
        "Спасибо, что выбрали Uclinic! 💙\n\n"
        "Мы были бы рады узнать ваше мнение о посещении."
    )
    
    if procedure_name:
        message += f"\n\nКак вам процедура \"{procedure_name}\"?"
    else:
        message += "\n\nКак вам ваше посещение?"
    
    message += "\n\nОцените от 1 до 5:"
    
    return message


def format_survey_thanks(rating: int) -> str:
    """Благодарность после опроса"""
    if rating == 5:
        return (
            "Спасибо за высокую оценку! ⭐⭐⭐⭐⭐\n\n"
            "Мы были бы очень благодарны, если бы вы оставили отзыв в Яндекс.Картах!"
        )
    elif rating >= 4:
        return "Спасибо за вашу оценку! Рады, что вам понравилось! 😊"
    elif rating >= 3:
        return "Спасибо за обратную связь! Мы всегда работаем над улучшением сервиса."
    else:
        return (
            "Спасибо за честную оценку. "
            "Мы сожалеем, что не оправдали ваших ожиданий. "
            "Наша команда обязательно свяжется с вами для решения вопроса."
        )

