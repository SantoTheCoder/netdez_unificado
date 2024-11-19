# remarketing_handler.py
import json
import os
import logging
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, Application
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

from remarketing_config import (
    DISCOUNT_PERCENTAGE,
    REMARKETING_DELAY_HOURS,
    OFFER_VALIDITY_HOURS,
    PROMOTIONAL_IMAGE,
    PROMOTIONAL_TEXT,
    REMARKETING_CHECK_INTERVAL_SECONDS
)

logger = logging.getLogger(__name__)

ABANDONMENT_FILE = 'abandono_pix.json'

def record_abandonment(user_id, pix_id):
    """Registra um evento de abandono de PIX garantindo um único registro por usuário"""
    abandonment_data = {
        'user_id': user_id,
        'pix_id': pix_id,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'remarketing_enviado': False,
        'offer_sent_timestamp': None
    }

    if os.path.exists(ABANDONMENT_FILE):
        with open(ABANDONMENT_FILE, 'r+') as file:
            data = json.load(file)
            # Verifica se já existe um abandono para o user_id
            for entry in data:
                if entry['user_id'] == user_id:
                    logger.info(f"Abandono já registrado para o usuário {user_id}. Não será duplicado.")
                    return  # Não adiciona um novo abandono

            # Se não existir, adiciona o novo abandono
            data.append(abandonment_data)
            file.seek(0)
            json.dump(data, file, indent=4)
    else:
        with open(ABANDONMENT_FILE, 'w') as file:
            json.dump([abandonment_data], file, indent=4)

    logger.info(f"Abandono registrado para o usuário {user_id}")

def remove_abandonment(user_id):
    """Remove o registro de abandono para um usuário"""
    if os.path.exists(ABANDONMENT_FILE):
        with open(ABANDONMENT_FILE, 'r+') as file:
            data = json.load(file)
            data = [entry for entry in data if entry['user_id'] != user_id]
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

    logger.info(f"Abandono removido para o usuário {user_id}")

async def send_remarketing_offers(application: Application):
    """Verifica periodicamente e envia ofertas de remarketing"""
    logger.info("Verificando ofertas de remarketing para enviar...")
    if os.path.exists(ABANDONMENT_FILE):
        with open(ABANDONMENT_FILE, 'r+') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao ler o arquivo JSON: {e}")
                return

            updated_data = []
            for entry in data:
                try:
                    user_id = entry['user_id']
                    timestamp = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                    remarketing_enviado = entry['remarketing_enviado']
                    time_since_abandonment = datetime.now() - timestamp

                    logger.info(f"Processando usuário {user_id} para remarketing...")
                    if not remarketing_enviado and time_since_abandonment >= timedelta(hours=REMARKETING_DELAY_HOURS):
                        # Envia a mensagem de remarketing
                        await send_remarketing_message(user_id, application)
                        entry['remarketing_enviado'] = True
                        entry['offer_sent_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        logger.info(f"Oferta de remarketing enviada para o usuário {user_id}")

                    elif remarketing_enviado:
                        # Verifica se a validade da oferta expirou
                        offer_sent_timestamp_str = entry.get('offer_sent_timestamp')
                        if offer_sent_timestamp_str:
                            offer_sent_timestamp = datetime.strptime(offer_sent_timestamp_str, '%Y-%m-%d %H:%M:%S')
                            time_since_offer_sent = datetime.now() - offer_sent_timestamp
                            if time_since_offer_sent >= timedelta(hours=OFFER_VALIDITY_HOURS):
                                logger.info(f"Oferta expirada para o usuário {user_id}, removendo entrada.")
                                continue  # Não adiciona esta entrada ao updated_data
                        else:
                            # Se não houver offer_sent_timestamp, remove a entrada
                            logger.info(f"Entrada inválida para o usuário {user_id}, removendo entrada.")
                            continue  # Não adiciona esta entrada ao updated_data

                    updated_data.append(entry)
                except Exception as e:
                    logger.error(f"Erro ao processar a entrada de abandono para usuário {entry.get('user_id')}: {e}")

            # Atualiza o arquivo JSON com dados processados
            with open(ABANDONMENT_FILE, 'w') as file:
                json.dump(updated_data, file, indent=4)
    else:
        logger.info("Nenhum arquivo de abandono encontrado.")

async def send_remarketing_message(user_id, application: Application, retries=3, delay=5):
    """Envia a mensagem de remarketing para o usuário com tentativas de reenvio"""
    attempt = 0
    while attempt < retries:
        try:
            # Cria botões para o remarketing
            keyboard = [
                [InlineKeyboardButton("Aproveitar Oferta - Plano Individual", callback_data='remarketing_offer_user')],
                [InlineKeyboardButton("Aproveitar Oferta - Revenda", callback_data='remarketing_offer_reseller')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            with open(PROMOTIONAL_IMAGE, 'rb') as image_file:
                await application.bot.send_photo(
                    chat_id=user_id,
                    photo=image_file,
                    caption=PROMOTIONAL_TEXT,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            logger.info(f"Oferta de remarketing enviada para o usuário {user_id}")
            return  # Sai do loop se o envio for bem-sucedido
        except Exception as e:
            attempt += 1
            logger.error(f"Erro ao enviar mensagem de remarketing para o usuário {user_id} (Tentativa {attempt}): {e}")
            if attempt < retries:
                await asyncio.sleep(delay)  # Espera antes de tentar novamente
            else:
                logger.error(f"Falha ao enviar mensagem para o usuário {user_id} após {retries} tentativas.")

async def handle_remarketing_offer(update, context):
    """Lida com o clique do usuário no botão da oferta de remarketing"""
    from payment_handlers import process_payment  # Importação dinâmica para evitar importação circular

    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id

    # Remove o registro de abandono para este usuário
    remove_abandonment(user_id)

    # Define o plano selecionado com base no botão clicado
    if query.data == 'remarketing_offer_user':
        # Plano individual atualizado com o novo nome do plano (exemplo: usuario_1_30)
        selected_plan = 'usuario_1_30'
    elif query.data == 'remarketing_offer_reseller':
        # Plano de revenda atualizado com o novo nome do plano (exemplo: revenda_start)
        selected_plan = 'revenda_start'

    # Verifica se a mensagem anterior é uma foto ou uma mensagem de texto
    try:
        await process_payment(update, context, discount=DISCOUNT_PERCENTAGE, plano_selecionado=selected_plan)
    except:
        # Caso não consiga editar, tenta enviar uma nova mensagem
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Clique abaixo para continuar com sua oferta exclusiva!",
            reply_markup=query.message.reply_markup,
            parse_mode='Markdown'
        )
        await process_payment(update, context, discount=DISCOUNT_PERCENTAGE, plano_selecionado=selected_plan)

def setup_remarketing_handlers(application):
    """Configura os handlers para o remarketing"""
    application.add_handler(CallbackQueryHandler(handle_remarketing_offer, pattern='^remarketing_offer_'))

def start_remarketing_task(scheduler, application):
    """Agenda a tarefa de remarketing periodicamente com intervalo definido em remarketing_config.py"""
    scheduler.add_job(
        send_remarketing_offers,
        trigger=IntervalTrigger(seconds=REMARKETING_CHECK_INTERVAL_SECONDS),
        args=[application],
        id='remarketing_periodic',
        replace_existing=True
    )
    logger.info(f"Tarefa de remarketing agendada para rodar a cada {REMARKETING_CHECK_INTERVAL_SECONDS} segundos.")
