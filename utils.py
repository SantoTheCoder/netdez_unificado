#utils.py
import requests
import logging
import random
import string
from config import API_KEY, TELEGRAM_CHAT_ID, URL_PAINEL_API  # Adiciona as importações necessárias

logger = logging.getLogger(__name__)

def make_request(data, url=URL_PAINEL_API):
    try:
        response = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data)
        response.raise_for_status()
        return response.text  # Alterado para retornar o texto da resposta
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return f"Error: {str(e)}"

def generate_random_string(length=11):  # Corrigido para garantir 11 caracteres
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))  # Inclui letras e números

def notify_telegram(message, chat_id=TELEGRAM_CHAT_ID, pin_message=False):
    url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': "Markdown",
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info(f"Message sent to Telegram: {message}")
        
        if pin_message:
            message_id = response.json().get("result", {}).get("message_id")
            if message_id:
                pin_url = f"https://api.telegram.org/bot{API_KEY}/pinChatMessage"
                pin_data = {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'disable_notification': True
                }
                pin_response = requests.post(pin_url, data=pin_data)
                pin_response.raise_for_status()
                logger.info(f"Message pinned to Telegram: {message_id}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Telegram: {e}")
