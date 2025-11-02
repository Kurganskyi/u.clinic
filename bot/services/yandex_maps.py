"""
Генерация ссылок на Яндекс.Карты с предзаполненным текстом отзыва
"""
import urllib.parse
from typing import Optional


def generate_yandex_maps_review_link(
    organization_name: str = "Uclinic",
    procedure_name: str = "",
    prefill_text: str = None
) -> str:
    """
    Генерация ссылки на Яндекс.Карты для отзыва
    
    Args:
        organization_name: Название организации
        procedure_name: Название процедуры
        prefill_text: Предзаполненный текст (если не указан, используется шаблон)
    
    Returns:
        URL для отзыва в Яндекс.Картах
    """
    if prefill_text is None:
        if procedure_name:
            prefill_text = f"Я прошла процедуру {procedure_name} и мне очень понравилось! "
        else:
            prefill_text = "Я была в клинике и мне очень понравилось! "
        prefill_text += "Рекомендую!"
    
    # Кодируем текст для URL
    encoded_text = urllib.parse.quote(prefill_text)
    
    # Формируем ссылку на Яндекс.Карты
    # Формат: https://yandex.ru/maps/-/org/{org_id}/reviews с параметром text
    # Альтернативный вариант через поиск организации
    base_url = "https://yandex.ru/maps"
    
    # Поиск организации + параметр для отзыва
    search_query = urllib.parse.quote(organization_name)
    url = f"{base_url}/?text={search_query}&add-review=true&review-text={encoded_text}"
    
    return url

