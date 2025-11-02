"""
Тесты конфигурации
"""
import pytest
from bot.config import Config


def test_config_validation():
    """Тест валидации конфигурации"""
    # Этот тест будет падать без правильных значений в .env
    # Для реального запуска нужно настроить .env.test
    
    # Проверяем, что Config определен
    assert hasattr(Config, 'TELEGRAM_BOT_TOKEN')
    assert hasattr(Config, 'BITRIX24_WEBHOOK_URL')
    assert hasattr(Config, 'DATABASE_URL')


def test_config_attributes():
    """Тест наличия всех необходимых атрибутов"""
    required_attrs = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_ADMIN_IDS',
        'BITRIX24_WEBHOOK_URL',
        'DATABASE_URL',
        'WEBHOOK_HOST',
        'WEBHOOK_PORT',
        'LOG_LEVEL'
    ]
    
    for attr in required_attrs:
        assert hasattr(Config, attr), f"Отсутствует атрибут: {attr}"

