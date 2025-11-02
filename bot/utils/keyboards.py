"""
Клавиатуры для Telegram-бота
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def get_reminder_keyboard():
    """Клавиатура для напоминания за 24 часа"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, приду", callback_data="reminder_confirm"),
            InlineKeyboardButton("❌ Нет, не получается", callback_data="reminder_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_survey_keyboard():
    """Клавиатура для опроса (оценка 1-5)"""
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="survey_1"),
            InlineKeyboardButton("2", callback_data="survey_2"),
            InlineKeyboardButton("3", callback_data="survey_3"),
            InlineKeyboardButton("4", callback_data="survey_4"),
            InlineKeyboardButton("5 ⭐", callback_data="survey_5")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_main_menu_keyboard():
    """Главное меню бота (базовое, будет расширено после тестирования @Uclinic1Bot)"""
    keyboard = [
        [KeyboardButton("📅 Записаться")],
        [KeyboardButton("📋 Акции"), KeyboardButton("💰 Цены")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("📞 Контакты")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

