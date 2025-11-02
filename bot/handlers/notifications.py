"""
Обработчики уведомлений о записях
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session

from bot.database import SessionLocal
from bot.models import User, Appointment
from bot.services.bitrix24 import Bitrix24Client
from bot.utils.messages import format_appointment_notification, format_reminder_24h, format_survey_message
from bot.utils.keyboards import get_reminder_keyboard, get_survey_keyboard
from bot.config import Config

logger = logging.getLogger(__name__)

# Ленивая инициализация клиента Битрикс24
_bitrix_client = None

def get_bitrix_client():
    """Получение экземпляра клиента Битрикс24 (создаём при первом вызове)"""
    global _bitrix_client
    if _bitrix_client is None:
        _bitrix_client = Bitrix24Client()
    return _bitrix_client

# Глобальные переменные для доступа к боту и планировщику (устанавливаются в main.py)
_app_bot = None
_app_scheduler = None


def set_bot_application(bot, scheduler):
    """Установка экземпляра бота и планировщика для использования в обработчиках"""
    global _app_bot, _app_scheduler
    _app_bot = bot
    _app_scheduler = scheduler


def handle_bitrix24_webhook(webhook_data: Dict) -> bool:
    """
    Обработка вебхука от Битрикс24
    
    Args:
        webhook_data: Данные вебхука от Битрикс24
        
    Returns:
        True если успешно обработано, False в противном случае
    """
    event = webhook_data.get('event')
    data = webhook_data.get('data', {})
    
    if event == 'ONCRMDEALADD':
        # Создана новая сделка (запись)
        deal_id = data.get('FIELDS', {}).get('ID')
        if deal_id:
            logger.info(f"Получен вебхук ONCRMDEALADD для сделки {deal_id}")
            return process_new_appointment(int(deal_id))
    
    elif event == 'ONCRMDEALUPDATE':
        # Обновлена существующая сделка
        deal_id = data.get('FIELDS', {}).get('ID')
        if deal_id:
            logger.info(f"Получен вебхук ONCRMDEALUPDATE для сделки {deal_id}")
            return update_appointment(int(deal_id))
    
    return False


def process_new_appointment(deal_id: int) -> bool:
    """
    Обработка новой записи из Битрикс24
    
    Args:
        deal_id: ID сделки в Битрикс24
        
    Returns:
        True если успешно, False в противном случае
    """
    db: Session = SessionLocal()
    
    try:
        # Получаем данные о сделке из Битрикс24
        bitrix_client = get_bitrix_client()
        deal = bitrix_client.get_deal(deal_id)
        if not deal:
            logger.error(f"Не удалось получить данные сделки {deal_id}")
            return False
        
        # Извлекаем данные
        appointment_date_str = deal.get('BEGINDATE') or deal.get('UF_CRM_APPOINTMENT_DATE')
        if not appointment_date_str:
            logger.warning(f"У сделки {deal_id} не указана дата записи")
            return False
        
        # Парсим дату (формат может быть разным)
        try:
            appointment_date = datetime.fromisoformat(appointment_date_str.replace('Z', '+00:00'))
        except:
            # Альтернативный формат
            appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d %H:%M:%S')
        
        # Получаем данные
        phone = deal.get('PHONE', [])
        phone_number = phone[0] if phone else None
        
        procedure_name = deal.get('TITLE') or deal.get('UF_CRM_PROCEDURE_NAME')
        doctor_name = deal.get('ASSIGNED_BY_ID')  # TODO: Получить имя через contact.get
        
        # Ищем пользователя по телефону
        user = None
        if phone_number:
            user = db.query(User).filter(User.phone_number == phone_number).first()
        
        # Создаем запись в БД
        appointment = Appointment(
            bitrix24_deal_id=deal_id,
            user_id=user.id if user else None,
            phone_number=phone_number,
            appointment_date=appointment_date,
            procedure_name=procedure_name,
            doctor_name=str(doctor_name) if doctor_name else None,
            notification_sent=False
        )
        db.add(appointment)
        db.commit()
        
        # Отправляем уведомление клиенту (если есть пользователь)
        if user and _app_bot:
            send_appointment_notification(user.telegram_id, appointment, db, bot=_app_bot)
        
        # Планируем напоминание за 24 часа
        if _app_scheduler:
            _app_scheduler.schedule_reminder(
                appointment.id,
                appointment_date,
                send_reminder_24h,
                bot=_app_bot
            )
            
            # Планируем опрос через 3 дня
            _app_scheduler.schedule_survey(
                appointment.id,
                appointment_date,
                send_survey,
                bot=_app_bot
            )
        
        logger.info(f"Обработана новая запись {appointment.id} из Битрикс24 сделки {deal_id}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка обработки новой записи {deal_id}: {e}", exc_info=True)
        db.rollback()
        return False
    
    finally:
        db.close()


def update_appointment(deal_id: int) -> bool:
    """Обновление существующей записи"""
    db: Session = SessionLocal()
    
    try:
        appointment = db.query(Appointment).filter(
            Appointment.bitrix24_deal_id == deal_id
        ).first()
        
        if not appointment:
            logger.warning(f"Запись для сделки {deal_id} не найдена в БД")
            return False
        
        # Получаем обновленные данные из Битрикс24
        bitrix_client = get_bitrix_client()
        deal = bitrix_client.get_deal(deal_id)
        if not deal:
            return False
        
        # Обновляем поля
        # TODO: Реализовать обновление полей
        
        db.commit()
        return True
    
    except Exception as e:
        logger.error(f"Ошибка обновления записи {deal_id}: {e}", exc_info=True)
        db.rollback()
        return False
    
    finally:
        db.close()


def send_appointment_notification(telegram_id: int, appointment: Appointment, db: Session, bot=None):
    """
    Отправка уведомления о записи клиенту
    
    Args:
        telegram_id: Telegram ID пользователя
        appointment: Объект записи
        db: Сессия БД
        bot: Экземпляр бота (опционально)
    """
    if not bot:
        logger.warning(f"Бот не передан для отправки уведомления пользователю {telegram_id}")
        return
    
    try:
        message_text = format_appointment_notification(
            appointment_date=appointment.appointment_date,
            doctor_name=appointment.doctor_name,
            procedure_name=appointment.procedure_name
        )
        
        # Отправка сообщения через бота (синхронно, т.к. вызывается из обработчика вебхука)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(bot.send_message(
            chat_id=telegram_id,
            text=message_text
        ))
        
        loop.close()
        
        # Отмечаем, что уведомление отправлено
        appointment.notification_sent = True
        db.commit()
        logger.info(f"Уведомление отправлено пользователю {telegram_id} о записи {appointment.id}")
    
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления пользователю {telegram_id}: {e}", exc_info=True)
        db.rollback()


async def send_reminder_24h(appointment_id: int, bot=None):
    """Отправка напоминания за 24 часа"""
    if not bot:
        logger.warning(f"Бот не передан для отправки напоминания записи {appointment_id}")
        return
    
    db = SessionLocal()
    
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            logger.warning(f"Запись {appointment_id} не найдена")
            return
        
        if appointment.reminder_sent:
            logger.info(f"Напоминание для записи {appointment_id} уже было отправлено")
            return
        
        user = appointment.user
        if not user:
            logger.warning(f"Пользователь не найден для записи {appointment_id}")
            return
        
        message_text = format_reminder_24h(
            appointment_date=appointment.appointment_date,
            doctor_name=appointment.doctor_name,
            procedure_name=appointment.procedure_name
        )
        
        keyboard = get_reminder_keyboard()
        
        # Сохраняем appointment_id в user_data для обработки callback
        # TODO: Передать appointment_id в callback_data кнопок
        
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message_text,
            reply_markup=keyboard
        )
        
        appointment.reminder_sent = True
        db.commit()
        logger.info(f"Напоминание отправлено пользователю {user.telegram_id} для записи {appointment_id}")
    
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания для записи {appointment_id}: {e}", exc_info=True)
        db.rollback()
    
    finally:
        db.close()


async def send_survey(appointment_id: int, bot=None):
    """Отправка опроса через 3 дня"""
    if not bot:
        logger.warning(f"Бот не передан для отправки опроса записи {appointment_id}")
        return
    
    db = SessionLocal()
    
    try:
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            logger.warning(f"Запись {appointment_id} не найдена")
            return
        
        # Проверяем, не отменил ли клиент запись
        if appointment.reminder_confirmed is False:
            logger.info(f"Клиент отменил запись {appointment_id}, опрос не отправляем")
            return
        
        user = appointment.user
        if not user:
            logger.warning(f"Пользователь не найден для записи {appointment_id}")
            return
        
        # Проверяем, не был ли уже отправлен опрос
        from bot.models import Survey
        existing_survey = db.query(Survey).filter(
            Survey.appointment_id == appointment_id,
            Survey.user_id == user.id
        ).first()
        
        if existing_survey:
            logger.info(f"Опрос для записи {appointment_id} уже был отправлен")
            return
        
        message_text = format_survey_message(procedure_name=appointment.procedure_name)
        keyboard = get_survey_keyboard()
        
        await bot.send_message(
            chat_id=user.telegram_id,
            text=message_text,
            reply_markup=keyboard
        )
        
        # Создаем запись опроса
        survey = Survey(
            appointment_id=appointment_id,
            user_id=user.id,
            sent_at=datetime.utcnow()
        )
        db.add(survey)
        db.commit()
        logger.info(f"Опрос отправлен пользователю {user.telegram_id} для записи {appointment_id}")
    
    except Exception as e:
        logger.error(f"Ошибка отправки опроса для записи {appointment_id}: {e}", exc_info=True)
        db.rollback()
    
    finally:
        db.close()

