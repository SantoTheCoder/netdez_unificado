# broadcast.py
import logging
import asyncio
from telegram import Update, InputFile
from telegram.ext import ContextTypes, CommandHandler
from database import get_db_connection  # Usando o seu sistema de database existente
from config import ADMIN_ID  # Certifique-se de definir o ID do admin no seu config.py
import requests
import os

logger = logging.getLogger(__name__)

async def send_broadcast_message(context, chat_id, message):
    """Função auxiliar para enviar uma mensagem a um usuário específico"""
    try:
        if message.photo:
            # Se a mensagem tiver uma imagem
            file_id = message.photo[-1].file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path

            response = requests.get(file_path)
            image_path = os.path.join("downloads", f"{file_id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(response.content)

            # Enviar a imagem com legenda, se houver
            caption = message.caption_html or message.caption or ""
            await context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'), caption=caption, parse_mode='HTML')
            os.remove(image_path)
        elif message.document:
            # Se a mensagem tiver um documento (arquivo)
            file_id = message.document.file_id
            file = await context.bot.get_file(file_id)
            file_path = file.file_path

            response = requests.get(file_path)
            document_path = os.path.join("downloads", message.document.file_name)
            with open(document_path, 'wb') as f:
                f.write(response.content)

            await context.bot.send_document(chat_id=chat_id, document=open(document_path, 'rb'))
            os.remove(document_path)
        elif message.text_html:
            # Se a mensagem for texto com formatação HTML
            await context.bot.send_message(chat_id=chat_id, text=message.text_html, parse_mode='HTML')
        elif message.text:
            # Se a mensagem for texto simples
            await context.bot.send_message(chat_id=chat_id, text=message.text, parse_mode='HTML')

        logger.info(f"Mensagem enviada para {chat_id}")
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem para {chat_id}: {e}")

async def execute_broadcast(context, message, users):
    """Função que executa o envio do broadcast para todos os usuários"""
    os.makedirs('downloads', exist_ok=True)

    for user in users:
        chat_id = user['chat_id']
        await send_broadcast_message(context, chat_id, message)
        await asyncio.sleep(1)  # Delay entre envios

    # Informa o administrador que o broadcast foi concluído
    await context.bot.send_message(chat_id=ADMIN_ID, text="Broadcast enviado com sucesso.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    message = update.message.reply_to_message
    if not message:
        await update.message.reply_text("Por favor, responda a uma mensagem para transmitir.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM users WHERE chat_id IS NOT NULL")
    users = cursor.fetchall()
    conn.close()

    if not users:
        logger.error("Nenhum usuário encontrado com chat_id válido.")
        await update.message.reply_text("Nenhum usuário encontrado para enviar a mensagem.")
        return

    # Dispara o broadcast em segundo plano sem alterar o fluxo existente
    asyncio.create_task(execute_broadcast(context, message, users))

    # Confirmação imediata ao administrador de que o broadcast foi iniciado
    await update.message.reply_text("Broadcast iniciado em segundo plano. O bot permanece ativo.")

def setup_broadcast_handlers(application):
    application.add_handler(CommandHandler("broadcast", broadcast))
