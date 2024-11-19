# faq.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import ContextTypes, CallbackQueryHandler
from remarketing_config import FAQ_VIDEO_FILES

logger = logging.getLogger(__name__)

# Textos dos tutoriais em Markdown HTML
FAQ_TEXTS = {
    'tutorial1': "<b>Internet Ilimitada Android</b>\nAssista ao vídeo para aprender a navegar sem limites.",
    'tutorial2': "<b>Sistema de Revendedores Android</b>\nEntenda como funciona o sistema de revenda. Veja o vídeo!",
    'tutorial3': "<b>Compras para Usuários e Revendedores</b>\nAprenda a realizar compras de forma prática.",
    'tutorial4': "<b>Autoatendimento e Conexão</b>\nResolva problemas de conexão para você e seus clientes com nosso vídeo sobre autoatendimento."
}

# Função para iniciar o FAQ a partir do botão do menu principal
async def faq_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User accessed FAQ")
    # Inicia o FAQ com o primeiro tutorial
    await send_tutorial(update, context, tutorial='tutorial1')

# Função para enviar um tutorial específico com base na configuração centralizada
async def send_tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE, tutorial: str):
    video_link = FAQ_VIDEO_FILES.get(tutorial)
    caption_text = FAQ_TEXTS.get(tutorial)

    # Define os botões de navegação com base no tutorial atual
    if tutorial == 'tutorial1':
        keyboard = [[InlineKeyboardButton("Próximo Tutorial >>", callback_data='tutorial2')]]
    elif tutorial == 'tutorial2':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial1'),
             InlineKeyboardButton("Mais Informações >>", callback_data='tutorial3')]
        ]
    elif tutorial == 'tutorial3':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial2'),
             InlineKeyboardButton("Dica Master >>", callback_data='tutorial4')]
        ]
    elif tutorial == 'tutorial4':
        keyboard = [
            [InlineKeyboardButton("<< Anterior", callback_data='tutorial3'),
             InlineKeyboardButton("Menu Principal >>", callback_data='main_menu')]
        ]
    else:
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

# Handler para a navegação do FAQ usando callback queries
async def faq_navigation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'main_menu':
        # Apaga a mensagem do FAQ antes de redirecionar para o menu principal
        await query.message.delete()
        
        # Redireciona para o menu principal usando a função start_command
        from menu import start_command
        await start_command(query, context)
    else:
        await send_tutorial(update, context, tutorial=query.data)

# Função para configurar os handlers do FAQ
def setup_faq_handlers(application):
    # Handler para o comando/botão inicial do FAQ
    application.add_handler(CallbackQueryHandler(faq_start, pattern='^faq$'))

    # Handler para navegação dentro do FAQ e redirecionamento para o menu principal
    application.add_handler(CallbackQueryHandler(faq_navigation_handler, pattern='^(tutorial[1-4]|main_menu)$'))
