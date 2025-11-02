"""
Сервис интеграции с Битрикс24
"""
import logging
import requests
from typing import Dict, Optional, List
from bot.config import Config

logger = logging.getLogger(__name__)


class Bitrix24Client:
    """Клиент для работы с Битрикс24 REST API"""
    
    def __init__(self):
        self.webhook_url = Config.BITRIX24_WEBHOOK_URL
        self.incoming_token = Config.BITRIX24_INCOMING_WEBHOOK_TOKEN
        
        if not self.webhook_url:
            raise ValueError("BITRIX24_WEBHOOK_URL не настроен")
    
    def _make_request(self, method: str, params: Dict = None) -> Optional[Dict]:
        """
        Выполнение запроса к Битрикс24 API
        
        Args:
            method: Метод API (например, 'crm.deal.get')
            params: Параметры запроса
            
        Returns:
            Ответ API или None в случае ошибки
        """
        if params is None:
            params = {}
        
        url = f"{self.webhook_url}{method}"
        
        try:
            response = requests.post(url, json=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                logger.error(f"Ошибка Битрикс24 API: {result['error']}")
                return None
            
            return result.get('result')
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса к Битрикс24: {e}")
            return None
    
    def get_deal(self, deal_id: int) -> Optional[Dict]:
        """
        Получение информации о сделке
        
        Args:
            deal_id: ID сделки в Битрикс24
            
        Returns:
            Данные сделки или None
        """
        return self._make_request('crm.deal.get', {'id': deal_id})
    
    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """
        Получение информации о контакте
        
        Args:
            contact_id: ID контакта в Битрикс24
            
        Returns:
            Данные контакта или None
        """
        return self._make_request('crm.contact.get', {'id': contact_id})
    
    def update_deal(self, deal_id: int, fields: Dict) -> bool:
        """
        Обновление полей сделки
        
        Args:
            deal_id: ID сделки
            fields: Словарь полей для обновления
            
        Returns:
            True если успешно, False в противном случае
        """
        result = self._make_request('crm.deal.update', {
            'id': deal_id,
            'fields': fields
        })
        return result is not None
    
    def get_deals_by_phone(self, phone: str) -> List[Dict]:
        """
        Поиск сделок по номеру телефона
        
        Args:
            phone: Номер телефона (в любом формате)
            
        Returns:
            Список сделок
        """
        # Нормализация номера телефона
        phone_clean = ''.join(filter(str.isdigit, phone))
        
        # Поиск через фильтр
        result = self._make_request('crm.deal.list', {
            'filter': {'PHONE': phone_clean},
            'select': ['*', 'UF_*']
        })
        
        return result if result else []

