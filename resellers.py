# RESELLERS.PY
import logging
from config import IOS_API_KEY, DEFAULT_RESELLER_LIMIT, ADMIN_ID, API_KEY, TELEGRAM_CHAT_ID, URL_RESELLERS, SUPPORT_CONTACT, ANDROID_APP_LINK, IOS_APP_LINK
from utils import make_request, generate_random_string
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

def notify_telegram(message, chat_id=TELEGRAM_CHAT_ID, pin_message=False):
    url = f"https://api.telegram.org/bot{API_KEY}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': "HTML",
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

def create_reseller(limit=DEFAULT_RESELLER_LIMIT, username=None, password=None, notify=True):
    if username is None:
        username = generate_random_string(6)  # Gera nome de usuário com 6 caracteres
    if password is None:
        password = generate_random_string(6)  # Gera senha com 6 caracteres

    data = {
        'passapi': IOS_API_KEY,
        'module': 'createrev',
        'user': username,
        'pass': password,
        'admincid': 1,  # Ajuste conforme necessário
        'userlimite': limit,
        'whatsapp': "1234567890"
    }

    result = make_request(data)

    if 'error' not in result:
        success_message = (
            "<b>🎉✨ Revendedor Criado com Sucesso! Bem-vindo à Família! 🎉✨</b>\n\n"
            f"🔎 <b>Usuário:</b> <code>{username}</code>\n"
            f"🔑 <b>Senha:</b> <code>{password}</code>\n"
            f"🏆 <b>Validade:</b> <code>30 dias</code>\n"
            f"🕟 <b>Limite de Conexões:</b> <code>{limit}</code>\n\n"
            "🌟 <b>Obrigado por confiar em nossos serviços! Estamos aqui para você!</b>\n\n"
            f"🔗 <b>Painel de Acesso:</b> <a href=\"{URL_RESELLERS}\">Clique Aqui</a>\n"
            f"📞 <b>Suporte:</b> {SUPPORT_CONTACT}\n\n"
            "---\n\n"
            "<b>📱 Aplicativos e Arquivos de Configuração:</b>\n"
            f"- 📱 <b>Android:</b> <a href=\"{ANDROID_APP_LINK}\">Baixe Aqui</a>\n"
            f"- 🍎 <b>iOS:</b> <a href=\"{IOS_APP_LINK}\">Baixe Aqui</a>\n\n"
            "---\n\n"
            "<b>🛠️ Material de Apoio:</b>\n"
            "🖼️ <b>Material Publicitário:</b> @BANNERS_NET_ILIMITADA\n"
            "🎥 <b>Vídeos de Suporte:</b> @Kriasys_Autorizado >> Opção 5 (Auto Suporte Inteligente)\n\n"
            "---\n\n"
            "<b>💡 Dica Importante:</b>\n"
            "⚙️ <b>Acesse o Painel e configure sua conta de recebimento automático.</b>\n\n"
            "📌 <b>Com isso, seus clientes poderão:</b>\n"
            "- 🛒 Comprar <b>planos e revendas</b>;\n"
            "- 🚀 Criar <b>testes automáticos</b>;\n"
            "- 🔄 Efetuar <b>renovações automáticas</b>.\n\n"
            "🔒 <b>Eles pagam direto na sua conta, com total segurança e rapidez!</b>\n\n"
            "---\n\n"
            "❓ <b>Dúvidas?</b>\n"
            "📲 Fale com nosso suporte e tire todas as suas dúvidas! Estamos aqui para ajudar!\n\n"
            "🚀 <b>Conte conosco para alavancar seu negócio!</b>"
        )

        # Notifica ao canal apenas se `notify` for True
        if notify:
            notify_telegram(success_message)
            logger.info(success_message)

            # Adicionando informações financeiras na notificação ao canal
            sale_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            sale_value = 1  # Substitua pelo valor real da revenda, se necessário
            buyer_username = "comprador_teste_revenda"  # Substitua pelo nome de usuário do revendedor
            buyer_name = "Nome Teste Revenda"  # Substitua pelo nome real do revendedor

            financial_message = (
                "<b>🎉 Detalhes da Revenda 🎉</b>\n\n"
                f"<b>⏰ Data da Venda:</b> {sale_date}\n"
                f"<b>💵 Valor:</b> R$ {sale_value:.2f}\n"
                f"<b>👤 Comprador:</b> {buyer_username}\n"
                f"<b>💼 Nome:</b> {buyer_name}\n\n"
                "Revendedor criado com sucesso!"
            )
            notify_telegram(financial_message)
            logger.info(financial_message)

        return username, success_message  # Retorna o username junto com a mensagem
    else:
        error_message = f"Erro ao criar revendedor: {result}"
        if notify:
            notify_telegram(error_message)
        logger.error(error_message)
        return None, error_message

# Função de comando do Telegram para criar revendedor
async def create_reseller_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.", parse_mode="HTML")
        return
    
    logger.info("Received /createreseller command")
    
    # Gerar usuário e senha aleatórios
    username = generate_random_string(6)
    password = generate_random_string(6)
    
    # Criar o revendedor sem notificar o canal
    username, reseller_info = create_reseller(username=username, password=password, notify=False)
    
    if update.message:
        await update.message.reply_text(reseller_info, parse_mode="HTML", disable_web_page_preview=True)
    elif update.callback_query:
        await update.callback_query.edit_message_text(reseller_info, parse_mode="HTML", disable_web_page_preview=True)
