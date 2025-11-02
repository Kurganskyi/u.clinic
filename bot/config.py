"""
Конфигурация приложения
Все настройки загружаются из переменных окружения
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """Основные настройки приложения"""
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_IDS = [
        int(admin_id.strip()) 
        for admin_id in os.getenv('TELEGRAM_ADMIN_IDS', '').split(',')
        if admin_id.strip().isdigit()
    ]
    
    # Битрикс24
    BITRIX24_WEBHOOK_URL = os.getenv('BITRIX24_WEBHOOK_URL', '')
    BITRIX24_INCOMING_WEBHOOK_TOKEN = os.getenv('BITRIX24_INCOMING_WEBHOOK_TOKEN', '')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./bot.db')
    
    # Webhook Server
    WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5000'))
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
    
    # Scheduler
    SCHEDULER_TIMEZONE = os.getenv('SCHEDULER_TIMEZONE', 'Europe/Moscow')
    
    # Application
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Валидация обязательных параметров"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN не установлен")
        
        if not cls.BITRIX24_WEBHOOK_URL:
            errors.append("BITRIX24_WEBHOOK_URL не установлен")
        
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True

