"""
Точка входа для Telegram-бота Uclinic
"""
import logging
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from bot.config import Config
from bot.handlers.start import start_handler, help_handler
from bot.handlers.reminders import reminder_callback_handler
from bot.handlers.survey import survey_callback_handler
from bot.handlers.menu import (
    menu_handler, book_handler, promotions_handler, 
    prices_handler, contacts_handler
)
from bot.handlers.notifications import set_bot_application
from bot.database import init_db
from bot.services.scheduler import SchedulerService
from bot.services.webhook_server import run_webhook_server
from bot.utils.errors import error_handler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальный планировщик
scheduler_service = SchedulerService()


def main():
    """Запуск бота"""
    # Валидация конфигурации
    try:
        Config.validate()
        logger.info("Конфигурация валидна")
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return
    
    # Инициализация БД
    init_db()
    logger.info("База данных инициализирована")
    
    # Запуск планировщика
    scheduler_service.start()
    logger.info("Планировщик задач запущен")
    
    # Создание приложения
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Сохраняем ID администраторов для уведомлений об ошибках
    application.bot_data['admin_ids'] = Config.TELEGRAM_ADMIN_IDS
    application.bot_data['scheduler'] = scheduler_service
    
    # Устанавливаем бота и планировщик для обработчиков вебхуков
    # Используем initialize callback для доступа к боту
    async def initialize(application: Application):
        bot = application.bot
        set_bot_application(bot, scheduler_service)
        logger.info("Бот и планировщик установлены для обработчиков вебхуков")
    
    application.initialize = initialize
    
    # Регистрация handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("menu", menu_handler))
    
    # Обработчики callback-кнопок
    application.add_handler(CallbackQueryHandler(reminder_callback_handler, pattern="^reminder_"))
    application.add_handler(CallbackQueryHandler(survey_callback_handler, pattern="^survey_"))
    
    # Обработчики меню
    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.Regex("^📅 Записаться$"), book_handler))
    application.add_handler(MessageHandler(filters.Regex("^📋 Акции$"), promotions_handler))
    application.add_handler(MessageHandler(filters.Regex("^💰 Цены$"), prices_handler))
    application.add_handler(MessageHandler(filters.Regex("^❓ Помощь$"), help_handler))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), contacts_handler))
    
    # Глобальный обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск вебхук-сервера в отдельном потоке (если нужен)
    if Config.WEBHOOK_PORT > 0:
        webhook_thread = threading.Thread(
            target=run_webhook_server,
            daemon=True,
            name="WebhookServer"
        )
        webhook_thread.start()
        logger.info(f"Вебхук-сервер запущен на порту {Config.WEBHOOK_PORT}")
    
    # Запуск бота
    logger.info("Бот запускается...")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        scheduler_service.shutdown()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    main()

