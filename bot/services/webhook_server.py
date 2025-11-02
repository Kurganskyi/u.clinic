"""
Flask сервер для приема вебхуков от Битрикс24
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from bot.config import Config
from bot.handlers.notifications import handle_bitrix24_webhook

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route('/webhook/bitrix24', methods=['POST'])
def bitrix24_webhook():
    """
    Эндпоинт для приема вебхуков от Битрикс24
    
    Ожидаемые события:
    - ONCRMDEALADD - создание сделки
    - ONCRMDEALUPDATE - обновление сделки
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Получен пустой вебхук от Битрикс24")
            return jsonify({"error": "Empty request"}), 400
        
        event = data.get('event')
        
        if not event:
            logger.warning("Вебхук без указания события")
            return jsonify({"error": "No event specified"}), 400
        
        # Проверка секрета (если настроен)
        if Config.WEBHOOK_SECRET:
            received_secret = request.headers.get('X-Webhook-Secret')
            if received_secret != Config.WEBHOOK_SECRET:
                logger.warning("Неверный секрет вебхука")
                return jsonify({"error": "Invalid secret"}), 401
        
        # Обработка вебхука
        logger.info(f"Получен вебхук: {event}")
        
        # Асинхронная обработка через очередь или напрямую
        # Для MVP используем прямую обработку
        result = handle_bitrix24_webhook(data)
        
        if result:
            return jsonify({"status": "ok"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to process webhook"}), 500
    
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check эндпоинт"""
    return jsonify({
        "status": "ok",
        "service": "uclinic-bot-webhook"
    }), 200


def run_webhook_server():
    """Запуск Flask сервера для вебхуков"""
    app.run(
        host=Config.WEBHOOK_HOST,
        port=Config.WEBHOOK_PORT,
        debug=Config.DEBUG
    )

