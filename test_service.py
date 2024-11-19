# test_service.py
import json
import os
import logging
import requests
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import (
    CHANNEL_ID, CHANNEL_USERNAME, APP_MESSAGE_ID, URL_PAINEL_API, 
    IOS_API_KEY, ANDROID_APP_LINK, IOS_APP_LINK, RENEWAL_LINK
)
from users import create_user

logger = logging.getLogger(__name__)

# Arquivo JSON para registrar os testes gratuitos
TEST_RECORD_FILE = 'test_records.json'

def load_test_records():
    if os.path.exists(TEST_RECORD_FILE):
        with open(TEST_RECORD_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_test_records(records):
    with open(TEST_RECORD_FILE, 'w') as file:
        json.dump(records, file, indent=4)

def check_user_eligibility(user_id):
    records = load_test_records()
    user_record = records.get(str(user_id))
    if user_record:
        last_test_date = datetime.strptime(user_record['last_test_date'], '%Y-%m-%d')
        if datetime.now() - last_test_date < timedelta(days=30):
            return False  # Usuário não é elegível, pois já fez um teste nos últimos 30 dias
    return True

def register_user_test(user_id):
    records = load_test_records()
    records[str(user_id)] = {
        'last_test_date': datetime.now().strftime('%Y-%m-%d')
    }
    save_test_records(records)

def reset_monthly():
    if datetime.now().day == 1:
        logger.info("Resetando registros de teste mensalmente...")
        save_test_records({})
        logger.info("Registros de teste resetados com sucesso.")

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_username(user_id):
    for _ in range(5):  # tenta até 5 vezes criar um nome de usuário único
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        username = f"teste_{suffix}"
        if not check_username_exists(username):
            return username
    raise ValueError("Não foi possível gerar um nome de usuário único.")

def check_username_exists(username):
    api_data = {
        'passapi': IOS_API_KEY,
        'module': 'userget',
        'user': username
    }
    try:
        response = requests.post(URL_PAINEL_API, data=api_data, timeout=10)
        response.raise_for_status()
        return "Sucess" in response.text  # Verifica se o usuário já existe na resposta da API
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao verificar usuário existente: {e}")
        return False

async def handle_test_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Solicitação de teste recebida de {user_id}")

    confirmation_message = (
        "🚀 <b>2 Horas de Internet Ilimitada – Grátis!</b>\n\n"
        "<b>Ao confirmar, você recebe:</b>\n"
        "- 🌐 <b>Navegação 100% ilimitada</b> por 2 horas!\n"
        "- 📲 <b>App Exclusivo</b> com acesso rápido e fácil.\n"
        "- 🔒 <b>Usuário e Senha Seguros</b>, criados só para você.\n\n"
        "<b>💬 Suporte 24h:</b> Estamos sempre à disposição! E você ainda recebe vídeos tutoriais para aproveitar ao máximo o teste.\n\n"
        "<b>🎁 Bônus Especial: Indique e Ganhe!</b>\n"
        "Indique um amigo e ganhe <b>+30 dias grátis</b>. Quanto mais indicações, mais dias gratuitos você acumula!\n\n"
        "👉 <b>Confirme abaixo para começar seu teste gratuito!</b>"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Receber Teste Grátis", callback_data='confirmar_teste')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            confirmation_message, reply_markup=reply_markup, parse_mode="HTML"
        )
    elif update.message:
        await update.message.reply_text(
            confirmation_message, reply_markup=reply_markup, parse_mode="HTML"
        )

async def confirm_test_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Confirmação de teste recebida de {user_id}")

    if check_user_eligibility(user_id):
        try:
            username = generate_unique_username(user_id)
            password = generate_random_password()

            api_data = {
                'passapi': IOS_API_KEY,
                'module': 'criarteste',
                'user': username,
                'pass': password,
                'testtime': 120,  # Tempo do teste em minutos (2 horas)
                'admincid': 1,
                'userlimite': 1,
                'whatsapp': '',
                'validadeusuario': 0,
                'idpony': ''
            }

            response = requests.post(URL_PAINEL_API, data=api_data, timeout=10)
            response.raise_for_status()
            response_text = response.text
            logger.info(f"Resposta da API: {response_text}")

            if "Sucess" in response_text:
                register_user_test(user_id)
                logger.info(f"Usuário de teste {username} criado para {user_id}")
                await update.callback_query.message.delete()

                user_message = (
                    "<b>🎉 Usuário Criado com Sucesso! 🎉</b>\n\n"
                    "<b>🔎 Usuário:</b> <code>{USERNAME}</code>\n"
                    "<b>🔑 Senha:</b> <code>{PASSWORD}</code>\n"
                    "<b>🎯 Validade:</b> <code>2 horas a partir da ativação</code>\n"
                    "<b>🕟 Limite de Conexões:</b> <code>1</code>\n\n"
                    "<i>Você pode copiar o usuário ou a senha clicando em cima deles.</i>\n\n"
                    "<b>📱 Aplicativos e Arquivos de Configuração:</b>\n\n"
                    "- <b>Para Android:</b> <a href=\"{ANDROID_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n"
                    "- <b>Para iOS:</b> <a href=\"{IOS_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n\n"
                    "🌍 <a href=\"{RENEWAL_LINK}\">Link de Renovação (Clique Aqui)</a>\n"
                    "Use este link para realizar suas renovações futuras."
                ).format(
                    USERNAME=username,
                    PASSWORD=password,
                    ANDROID_APP_LINK=ANDROID_APP_LINK,
                    IOS_APP_LINK=IOS_APP_LINK,
                    RENEWAL_LINK=RENEWAL_LINK
                )

                await update.callback_query.message.reply_text(
                    user_message, parse_mode="HTML", disable_web_page_preview=True
                )

                # Encaminha a mensagem do canal com o aplicativo
                await context.bot.forward_message(
                    chat_id=update.callback_query.message.chat_id,
                    from_chat_id=CHANNEL_ID,
                    message_id=APP_MESSAGE_ID
                )

                # Mensagem de suporte
                support_message = (
                    "❓ <b>Ajuda Rápida:</b>\n\n"
                    "Nosso bot envia vídeos tutoriais 📽 e guias 📜. "
                    "Basta ir no Menu >> Dúvidas. Caso necessite, chame nosso suporte 24 horas. @kriasys_autorizado"
                )
                await update.callback_query.message.reply_text(
                    support_message, parse_mode="HTML"
                )
            else:
                logger.error(f"Erro na resposta da API: {response_text}")
                raise Exception("Erro ao criar teste na API")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar teste: {e}")
            await update.callback_query.message.reply_text(
                "Erro ao criar usuário de teste. Tente novamente mais tarde.",
                parse_mode="HTML"
            )
    else:
        logger.info(f"Usuário {user_id} já realizou um teste nos últimos 30 dias")
        await update.callback_query.message.reply_text(
            "Você já fez um teste gratuito nos últimos 30 dias. Por favor, aguarde para tentar novamente.",
            parse_mode="HTML"
        )

def setup_test_service_handlers(application):
    # Adiciona o handler para o botão de confirmação sem interferir com outros handlers
    application.add_handler(CallbackQueryHandler(confirm_test_request, pattern='^confirmar_teste$'))
