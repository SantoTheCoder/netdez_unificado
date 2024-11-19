# faq_ios.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from remarketing_config import FAQ_VIDEO_FILES

logger = logging.getLogger(__name__)

# Textos dos tutoriais em Markdown HTML
FAQ_TEXTS_IOS = {
    'tutorial1_ios': "<b>Internet Ilimitada iOS</b>\nAssista ao vídeo para aprender a navegar sem limites.",
    'tutorial2_ios': "<b>Sistema de Revendedores Android + iOS</b>\nEntenda como funciona o sistema de revenda. Veja o vídeo!",
    'tutorial3_ios': "<b>Compras para Usuários e Revendedores</b>\nAprenda a realizar compras de forma prática.",
    'tutorial4_ios': "<b>Autoatendimento e Conexão</b>\nResolva problemas de conexão para você e seus clientes com nosso vídeo sobre autoatendimento."
}

# Função para iniciar o FAQ iOS
async def faq_ios_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User accessed FAQ iOS")
    # Inicia o FAQ com o primeiro tutorial
    await send_tutorial_ios(update, context, tutorial='tutorial1_ios')

# Função para enviar um tutorial específico com base na configuração centralizada
async def send_tutorial_ios(update: Update, context: ContextTypes.DEFAULT_TYPE, tutorial: str):
    video_link = FAQ_VIDEO_FILES.get(tutorial)
    caption_text = FAQ_TEXTS_IOS.get(tutorial)

    # Define os botões de navegação com base no tutorial atual
    if tutorial == 'tutorial1_ios':
        keyboard = [[InlineKeyboardButton("Próximo Tutorial >>", callback_data='tutorial2_ios')]]
    elif tutorial == 'tutorial2_ios':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial1_ios'),
             InlineKeyboardButton("Mais Informações >>", callback_data='tutorial3_ios')]
        ]
    elif tutorial == 'tutorial3_ios':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial2_ios'),
             InlineKeyboardButton("Dica Master >>", callback_data='tutorial4_ios')]
        ]
    elif tutorial == 'tutorial4_ios':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial3_ios'),
             InlineKeyboardButton("Menu Principal >>", callback_data='start')]
        ]
    else:
        logger.warning(f"Tutorial inválido: {tutorial}")
        return

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Envia a mensagem com o vídeo e a legenda abaixo do vídeo
    if update.callback_query:
        await update.callback_query.message.delete()  # Apaga a mensagem anterior para evitar acúmulo
        await update.callback_query.message.reply_video(
            video=video_link,
            caption=caption_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_video(
            video=video_link,
            caption=caption_text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# Handler para a navegação do FAQ iOS usando callback queries
async def faq_ios_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start':
        # Apaga a mensagem do FAQ antes de redirecionar para o menu principal
        await query.message.delete()

        # Redireciona para o menu principal usando a função start_command
        from menu import start_command
        await start_command(query, context)
    else:
        # Envia o tutorial correspondente
        await send_tutorial_ios(update, context, tutorial=query.data)

# Função para configurar os handlers do FAQ iOS
def setup_faq_ios_handlers(application):
    # Handler para o botão inicial do FAQ iOS
    application.add_handler(CallbackQueryHandler(faq_ios_start, pattern='^faq_ios$'))

    # Handler para navegação dentro do FAQ iOS e redirecionamento para o menu principal
    application.add_handler(CallbackQueryHandler(faq_ios_navigation_handler, pattern='^(tutorial[1-4]_ios|start)$'))
