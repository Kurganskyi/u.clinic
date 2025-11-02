"""
Обработчики меню бота
Базовые команды на основе аудита @Uclinic1Bot
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.keyboards import get_main_menu_keyboard
from bot.utils.errors import handle_async_exceptions

logger = logging.getLogger(__name__)


@handle_async_exceptions
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    menu_text = (
        "📋 Главное меню Uclinic\n\n"
        "Выберите нужный раздел:"
    )
    keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(menu_text, reply_markup=keyboard)


@handle_async_exceptions
async def book_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Записаться'"""
    response_text = (
        "📅 Запись на приём\n\n"
        "Для записи на приём свяжитесь с нами:\n"
        "📞 +7 (XXX) XXX-XX-XX\n"
        "✉️ info@uclinic.ru\n\n"
        "Или оставьте заявку через бота — "
        "наш администратор свяжется с вами в ближайшее время."
    )
    await update.message.reply_text(response_text)


@handle_async_exceptions
async def promotions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Акции'"""
    response_text = (
        "🎁 Акции и спецпредложения Uclinic\n\n"
        "Следите за нашими акциями и не упустите выгодные предложения!\n\n"
        "📌 Всегда актуальная информация на сайте:\n"
        "u-clinic.ru/promo\n\n"
        "Акции могут обновляться. Проверяйте регулярно!"
    )
    await update.message.reply_text(response_text)


@handle_async_exceptions
async def prices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Цены'"""
    response_text = (
        "💰 Прайс-лист услуг\n\n"
        "Полный прайс-лист наших услуг доступен на сайте:\n"
        "u-clinic.ru/price\n\n"
        "Для уточнения стоимости конкретной процедуры "
        "свяжитесь с администратором."
    )
    await update.message.reply_text(response_text)


@handle_async_exceptions
async def contacts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Контакты'"""
    response_text = (
        "📞 Контактная информация\n\n"
        "Клиника экспертной косметологии Uclinic\n\n"
        "📍 Адрес:\n"
        "г. Тверь, ул. Примерная, д. 123\n\n"
        "📱 Телефон:\n"
        "+7 (XXX) XXX-XX-XX\n\n"
        "✉️ Email:\n"
        "info@uclinic.ru\n\n"
        "🌐 Сайт:\n"
        "u-clinic.ru\n\n"
        "⏰ Режим работы:\n"
        "Пн-Сб: 09:00 - 21:00\n"
        "Вс: 10:00 - 20:00"
    )
    await update.message.reply_text(response_text)

