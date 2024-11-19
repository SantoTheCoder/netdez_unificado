# faq_android.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from remarketing_config import FAQ_VIDEO_FILES

logger = logging.getLogger(__name__)

# Textos dos tutoriais em Markdown HTML
FAQ_TEXTS_ANDROID = {
    'tutorial1_android': "<b>Internet Ilimitada Android</b>\nAssista ao vídeo para aprender a navegar sem limites.",
    'tutorial2_android': "<b>Sistema de Revendedores Android</b>\nEntenda como funciona o sistema de revenda. Veja o vídeo!",
    'tutorial3_android': "<b>Compras para Usuários e Revendedores</b>\nAprenda a realizar compras de forma prática.",
    'tutorial4_android': "<b>Autoatendimento e Conexão</b>\nResolva problemas de conexão para você e seus clientes com nosso vídeo sobre autoatendimento."
}

# Função para iniciar o FAQ Android
async def faq_android_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User accessed FAQ Android")
    # Inicia o FAQ com o primeiro tutorial
    await send_tutorial_android(update, context, tutorial='tutorial1_android')

# Função para enviar um tutorial específico com base na configuração centralizada
async def send_tutorial_android(update: Update, context: ContextTypes.DEFAULT_TYPE, tutorial: str):
    video_link = FAQ_VIDEO_FILES.get(tutorial)
    caption_text = FAQ_TEXTS_ANDROID.get(tutorial)

    # Define os botões de navegação com base no tutorial atual
    if tutorial == 'tutorial1_android':
        keyboard = [[InlineKeyboardButton("Próximo Tutorial >>", callback_data='tutorial2_android')]]
    elif tutorial == 'tutorial2_android':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial1_android'),
             InlineKeyboardButton("Mais Informações >>", callback_data='tutorial3_android')]
        ]
    elif tutorial == 'tutorial3_android':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial2_android'),
             InlineKeyboardButton("Dica Master >>", callback_data='tutorial4_android')]
        ]
    elif tutorial == 'tutorial4_android':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial3_android'),
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

# Handler para a navegação do FAQ Android usando callback queries
async def faq_android_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await send_tutorial_android(update, context, tutorial=query.data)

# Função para configurar os handlers do FAQ Android
def setup_faq_android_handlers(application):
    # Handler para o botão inicial do FAQ Android
    application.add_handler(CallbackQueryHandler(faq_android_start, pattern='^faq_android$'))

    # Handler para navegação dentro do FAQ Android e redirecionamento para o menu principal
    application.add_handler(CallbackQueryHandler(faq_android_navigation_handler, pattern='^(tutorial[1-4]_android|start)$'))
