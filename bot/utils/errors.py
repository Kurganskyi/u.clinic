"""
Обработка ошибок и исключений
"""
import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Если есть update, пытаемся отправить сообщение пользователю
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Извините, произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к администратору."
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    # Уведомляем администраторов
    if context.bot and hasattr(context, 'bot_data'):
        admin_ids = context.bot_data.get('admin_ids', [])
        for admin_id in admin_ids:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"❌ Ошибка в боте: {type(context.error).__name__}: {context.error}"
                )
            except Exception as e:
                logger.error(f"Не удалось уведомить администратора {admin_id}: {e}")


def handle_async_exceptions(func):
    """Декоратор для обработки исключений в асинхронных функциях"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper

