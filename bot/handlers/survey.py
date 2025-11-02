"""
Обработчики опросов после процедуры
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.database import SessionLocal
from bot.models import Appointment, Survey, User
from bot.services.yandex_maps import generate_yandex_maps_review_link
from bot.utils.messages import format_survey_thanks
from bot.utils.errors import handle_async_exceptions

logger = logging.getLogger(__name__)


@handle_async_exceptions
async def survey_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа на опрос (оценка 1-5)"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    # Извлекаем оценку из callback_data (survey_1, survey_2, ..., survey_5)
    rating = int(callback_data.split('_')[1])
    
    db = SessionLocal()
    
    try:
        # Находим пользователя
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if not user:
            await query.edit_message_text("Пользователь не найден.")
            return
        
        # Находим запись для опроса
        appointment_id = context.user_data.get('pending_survey_appointment_id')
        
        if appointment_id:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        else:
            # Ищем последнюю завершенную запись
            appointment = db.query(Appointment).filter(
                Appointment.user_id == user.id,
                Appointment.appointment_date < datetime.utcnow()
            ).order_by(Appointment.appointment_date.desc()).first()
        
        if not appointment:
            await query.edit_message_text("Не найдена запись для опроса.")
            return
        
        # Проверяем, не отвечал ли уже пользователь
        existing_survey = db.query(Survey).filter(
            Survey.appointment_id == appointment.id,
            Survey.user_id == user.id
        ).first()
        
        if existing_survey and existing_survey.answered_at:
            await query.edit_message_text("Вы уже ответили на этот опрос. Спасибо!")
            return
        
        # Создаем или обновляем опрос
        if existing_survey:
            survey = existing_survey
        else:
            survey = Survey(
                appointment_id=appointment.id,
                user_id=user.id,
                sent_at=datetime.utcnow()
            )
            db.add(survey)
        
        survey.rating = rating
        survey.answered_at = datetime.utcnow()
        
        # Если оценка 5, отправляем ссылку на Яндекс.Карты
        if rating == 5:
            survey.yandex_link_sent = True
            yandex_link = generate_yandex_maps_review_link(
                procedure_name=appointment.procedure_name or ""
            )
            
            thanks_message = format_survey_thanks(rating)
            await query.edit_message_text(
                f"{thanks_message}\n\n"
                f"[Оставить отзыв в Яндекс.Картах]({yandex_link})",
                parse_mode='Markdown'
            )
        else:
            thanks_message = format_survey_thanks(rating)
            await query.edit_message_text(thanks_message)
        
        db.commit()
        logger.info(f"Пользователь {user_id} поставил оценку {rating} для записи {appointment.id}")
    
    except Exception as e:
        logger.error(f"Ошибка обработки опроса: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при обработке ответа.")
        db.rollback()
    
    finally:
        db.close()

