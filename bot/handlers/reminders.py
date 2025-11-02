"""
Обработчики напоминаний за 24 часа
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import SessionLocal
from bot.models import Appointment
from bot.services.bitrix24 import Bitrix24Client
from bot.utils.errors import handle_async_exceptions

logger = logging.getLogger(__name__)

# Ленивая инициализация клиента Битрикс24
_bitrix_client = None

def get_bitrix_client():
    """Получение экземпляра клиента Битрикс24"""
    global _bitrix_client
    if _bitrix_client is None:
        _bitrix_client = Bitrix24Client()
    return _bitrix_client


@handle_async_exceptions
async def reminder_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа на напоминание (Да/Нет)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    db = SessionLocal()
    
    try:
        # Извлекаем appointment_id из callback_data или из данных запроса
        # TODO: Сохранять appointment_id в callback_data при создании кнопки
        
        # Временная заглушка - нужно будет передавать appointment_id
        appointment_id = context.user_data.get('pending_reminder_appointment_id')
        
        if not appointment_id:
            # Пытаемся найти последнюю запись пользователя
            from bot.models import User
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if user:
                appointment = db.query(Appointment).filter(
                    Appointment.user_id == user.id,
                    Appointment.reminder_sent == True,
                    Appointment.reminder_confirmed == None
                ).order_by(Appointment.appointment_date.desc()).first()
            else:
                appointment = None
        else:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        
        if not appointment:
            await query.edit_message_text("Не найдена запись для подтверждения.")
            return
        
        # Обработка ответа
        if callback_data == "reminder_confirm":
            appointment.reminder_confirmed = True
            appointment.reminder_answered_at = datetime.utcnow()
            
            # Обновляем статус в Битрикс24
            try:
                bitrix_client = get_bitrix_client()
                bitrix_client.update_deal(
                    appointment.bitrix24_deal_id,
                    {'UF_CRM_REMINDER_CONFIRMED': 'Y'}
                )
            except Exception as e:
                logger.error(f"Не удалось обновить Битрикс24: {e}")
            
            await query.edit_message_text("✅ Спасибо за подтверждение! Ждём вас в назначенное время.")
            logger.info(f"Пользователь {user_id} подтвердил запись {appointment.id}")
        
        elif callback_data == "reminder_cancel":
            appointment.reminder_confirmed = False
            appointment.reminder_answered_at = datetime.utcnow()
            
            # Обновляем статус в Битрикс24
            try:
                bitrix_client = get_bitrix_client()
                bitrix_client.update_deal(
                    appointment.bitrix24_deal_id,
                    {'UF_CRM_REMINDER_CONFIRMED': 'N', 'STAGE_ID': 'CANCELED'}  # TODO: Уточнить статусы
                )
            except Exception as e:
                logger.error(f"Не удалось обновить Битрикс24: {e}")
            
            await query.edit_message_text(
                "❌ Поняли. Запись отменена.\n\n"
                "Если хотите записаться на другое время, свяжитесь с нами."
            )
            logger.info(f"Пользователь {user_id} отменил запись {appointment.id}")
            
            # Отменяем запланированный опрос
            scheduler = context.application.bot_data.get('scheduler')
            if scheduler:
                scheduler.cancel_job(f"survey_{appointment.id}")
        
        db.commit()
    
    except Exception as e:
        logger.error(f"Ошибка обработки напоминания: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при обработке ответа.")
        db.rollback()
    
    finally:
        db.close()

