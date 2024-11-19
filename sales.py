# sales.py
from telegram import Update
from telegram.ext import ContextTypes
import logging
from datetime import datetime, timedelta
from utils import make_request, generate_random_string
from config import (
    IOS_API_KEY, IOS_APP_LINK, CONFIG_FILES_LINK, 
    ANDROID_APP_LINK, RENEWAL_LINK, CHANNEL_ID, APP_MESSAGE_ID
)

logger = logging.getLogger(__name__)

# Tabela de preços com variações de logins e durações
USER_PLANS = {
    ('1', '15'): {'preco': 10.00, 'dias': 15},
    ('1', '30'): {'preco': 17.00, 'dias': 30},
    ('1', '40'): {'preco': 20.00, 'dias': 40},
    ('2', '30'): {'preco': 27.00, 'dias': 30},
    ('3', '30'): {'preco': 37.00, 'dias': 30},
    ('4', '30'): {'preco': 47.00, 'dias': 30}
}

def create_user_for_sale(user_limit, validity_days, admincid=1):
    username = generate_random_string(11)
    password = generate_random_string(11)
    validity_date = (datetime.now() + timedelta(days=validity_days)).strftime("%d/%m/%Y")
    
    api_data = {
        'passapi': IOS_API_KEY,
        'module': 'criaruser',
        'user': username,
        'pass': password,
        'validadeusuario': validity_days,
        'userlimite': user_limit,
        'whatsapp': "1234567890",
        'admincid': admincid
    }

    result = make_request(api_data)

    if 'error' not in result:
        user_message = (
            "<b>🎉 Usuário Criado com Sucesso! 🎉</b>\n\n"
            "<b>🔎 Usuário:</b> <code>{USERNAME}</code>\n"
            "<b>🔑 Senha:</b> <code>{PASSWORD}</code>\n"
            "<b>🎯 Validade:</b> <code>{VALIDITY_DATE}</code>\n"
            "<b>🕟 Limite de Conexões:</b> <code>{USER_LIMIT}</code>\n\n"
            "<b>📱 Aplicativos e Arquivos de Configuração:</b>\n\n"
            "- <b>Para Android:</b> <a href=\"{ANDROID_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n"
            "- <b>Para iOS:</b> <a href=\"{IOS_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n\n"
            "🌍 <a href=\"{RENEWAL_LINK}\">Link de Renovação (Clique Aqui)</a>\n"
            "Use este link para realizar suas renovações futuras."
        ).format(
            USERNAME=username,
            PASSWORD=password,
            VALIDITY_DATE=validity_date,
            USER_LIMIT=user_limit,
            ANDROID_APP_LINK=ANDROID_APP_LINK,
            IOS_APP_LINK=IOS_APP_LINK,
            RENEWAL_LINK=RENEWAL_LINK
        )
        logger.info(f"Usuário {username} criado com sucesso.")
        return username, user_message
    else:
        logger.error(f"Erro ao criar o usuário {username}: {result}")
        return None, "Erro ao criar o usuário. Por favor, verifique manualmente."

def get_user_plan_price(user_limit, validity_days):
    """Retorna o preço de acordo com o limite de usuários e validade"""
    plan_key = (str(user_limit), str(validity_days))
    plan = USER_PLANS.get(plan_key)
    if plan:
        return plan['preco']
    else:
        logger.error(f"Plano não encontrado para {user_limit} logins e {validity_days} dias")
        return None

# Função de comando do Telegram para criar um usuário para venda com planos variáveis
async def create_user_for_sale_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    logger.info(f"Comando /createsale recebido de {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    args = context.args
    if len(args) >= 2:
        try:
            user_limit = int(args[0])
            validity_days = int(args[1])
        except ValueError:
            await update.message.reply_text("Uso inválido. Exemplo: /createsale 2 30")
            return
    else:
        user_limit = DEFAULT_USER_LIMIT
        validity_days = DEFAULT_VALIDITY_DAYS

    plan_price = get_user_plan_price(user_limit, validity_days)
    if plan_price is None:
        await update.message.reply_text("Plano não encontrado. Por favor, verifique o limite de logins e dias.")
        return

    username, user_message = create_user_for_sale(validity_days=validity_days, user_limit=user_limit)
    if username:
        # Envia a mensagem inicial com o usuário e senha
        await update.message.reply_text(user_message, parse_mode="HTML", disable_web_page_preview=True)
        
        # Mensagem adicional informativa
        additional_message = "<i>Você pode copiar o usuário ou a senha clicando em cima deles.</i>"
        await update.message.reply_text(additional_message, parse_mode="HTML")
        
        # Encaminha a mensagem do aplicativo
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=APP_MESSAGE_ID
        )

        # Mensagem final de suporte
        support_message = (
            "❓ <b>Ajuda Rápida:</b>\n\n"
            "Nosso bot envia vídeos tutoriais 📽 e guias 📜. Basta ir no Menu >> Dúvidas. "
            "Caso necessite, chame nosso suporte 24 horas. @Pedrooo"
        )
        await update.message.reply_text(support_message, parse_mode="HTML")
    else:
        await update.message.reply_text(user_message, parse_mode="HTML")
