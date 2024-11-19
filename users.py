#USERS.PY
import logging
from datetime import datetime, timedelta
from config import DEFAULT_VALIDITY_DAYS, DEFAULT_USER_LIMIT, IOS_API_KEY, ADMIN_ID, IOS_APP_LINK, CONFIG_FILES_LINK, ANDROID_APP_LINK, RENEWAL_LINK
from utils import make_request, generate_random_string
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Tabela de preços com variações de logins e durações
USER_PLANS = {
    (1, 15): {'preco': 10.00, 'dias': 15},
    (1, 30): {'preco': 17.00, 'dias': 30},
    (1, 40): {'preco': 20.00, 'dias': 40},
    (2, 30): {'preco': 27.00, 'dias': 30},
    (3, 30): {'preco': 37.00, 'dias': 30},
    (4, 30): {'preco': 47.00, 'dias': 30}
}

def get_user_plan_price(user_limit, validity_days):
    """Retorna o preço de acordo com o limite de usuários e validade"""
    plan_key = (user_limit, validity_days)
    plan = USER_PLANS.get(plan_key)
    if plan:
        return plan['preco']
    else:
        logger.error(f"Plano não encontrado para {user_limit} logins e {validity_days} dias")
        return None

def create_user(validity_days=DEFAULT_VALIDITY_DAYS, user_limit=DEFAULT_USER_LIMIT, admincid=1):
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
        'admincid': admincid  # Adicionado admincid ao conjunto de parâmetros
    }

    result = make_request(api_data)

    if 'error' not in result:
        user_message = (
            "<b>🎉 Usuário Criado com Sucesso! 🎉</b>\n\n"
            f"<b>🔎 Usuário:</b>\n<code>{username}</code>\n\n"
            f"<b>🔑 Senha:</b>\n<code>{password}</code>\n\n"
            f"<b>🎯 Validade:</b>\n<code>{validity_date}</code>\n\n"
            f"<b>🕟 Limite de Conexões:</b>\n<code>{user_limit}</code>\n\n"
            "<b>📱 Aplicativos e Arquivos de Configuração:</b>\n\n"
            f"- <b>Para Android:</b>\n"
            f"  - <a href=\"{ANDROID_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n\n"
            f"🌍 <a href=\"{RENEWAL_LINK}\">Link de Renovação (Clique Aqui)</a>\n"
            "Use este link para realizar suas renovações futuras."
        )
        logger.info(f'Usuário {username} criado com sucesso.')
        return username, user_message
    else:
        logger.error(f'Erro ao criar o usuário {username}: {result}')
        return None, f"Erro ao criar usuário: {result}"

# Função de comando do Telegram para criar um usuário com planos variáveis
async def create_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    logger.info(f"Comando /createuser recebido de {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    args = context.args
    if len(args) >= 2:
        try:
            user_limit = int(args[0])
            validity_days = int(args[1])
        except ValueError:
            await update.message.reply_text("Uso inválido. Exemplo: /createuser 2 30")
            return
    else:
        user_limit = DEFAULT_USER_LIMIT
        validity_days = DEFAULT_VALIDITY_DAYS

    plan_price = get_user_plan_price(user_limit, validity_days)
    if plan_price is None:
        await update.message.reply_text("Plano não encontrado. Por favor, verifique o limite de logins e dias.")
        return

    username, user_message = create_user(validity_days=validity_days, user_limit=user_limit)
    await update.message.reply_text(user_message, parse_mode="HTML", disable_web_page_preview=True)

# Função de comando do Telegram para criar um usuário de teste com 1 dia de validade
async def create_test_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    logger.info(f"Comando /createtest recebido de {user_id}")
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    logger.info("Executando /createtest command")
    username, user_message = create_user(validity_days=1)
    if username:
        logger.info(f"Usuário de teste {username} criado com sucesso")
    else:
        logger.error("Falha ao criar usuário de teste")
    await update.message.reply_text(user_message, parse_mode="HTML", disable_web_page_preview=True)
