# menu.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payment_handlers import process_payment, confirm_payment
from affiliate_system import affiliate_dashboard
import test_service
from faq_android import faq_android_start
from faq_ios import faq_ios_start

logger = logging.getLogger(__name__)

# Função para criar o menu principal
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Exibindo o menu principal")

    # Mensagem de boas-vindas com tema futurista
    message = (
        "✨ <b>Bem-vindo ao NetDez!</b> 🚀\n\n"
        "🌐 <b>Internet Ilimitada</b> para <b>Android & iOS</b> 📱💻\n\n"
        "⚡ <b>Ultra Velocidade</b> | <b>Conexão Ininterrupta</b>\n"
        "🔒 <b>Segurança Avançada</b> | <b>Suporte 24/7</b>\n\n"
        "🚀 Escolha sua opção:"
    )

    # Botões do menu principal organizados de forma mais estética
    keyboard = [
        [
            InlineKeyboardButton("🚀 Internet Ilimitada iOS & Android", callback_data='comprar_ios')
        ],
        [
            InlineKeyboardButton("💰 Seja um Revendedor", callback_data='revenda_menu'),
            InlineKeyboardButton("🎁 Ganhe 30 Dias Grátis", callback_data='afiliado')
        ],
        [
            InlineKeyboardButton("🆓 Teste Grátis", callback_data='teste_gratis'),
            InlineKeyboardButton("📞 Suporte", url='https://t.me/pedrooo')
        ],
        [
            InlineKeyboardButton("🔥 Turbine suas Redes Sociais", url='https://t.me/crescimentosocial_bot')
        ],
        [
            InlineKeyboardButton("❓ FAQ / Dúvidas Frequentes", callback_data='faq_menu')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Exibe o menu principal na resposta à mensagem ou callback query
    if update.message:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    elif update.callback_query:
        await update.callback_query.message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# Função para o sub-menu de compra de Internet Ilimitada
async def comprar_ios_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Exibindo o menu de Internet Ilimitada")

    # Mensagem persuasiva com formatação aprimorada
    message = (
        "<b>🔍 Escolha seu Plano:</b>\n"
        "📱 <b>Compatível com Android & iOS</b>\n\n"
        "✨ <b>Benefícios:</b>\n"
        "• ⚡ Ultra Velocidade\n"
        "• 🔒 Segurança Total\n"
        "• 🛠️ Fácil de Usar\n\n"
        "🚀 Inicie sua conexão ilimitada:"
    )

    # Botões dos planos de usuários organizados em duas colunas para melhor visualização
    keyboard = [
        [
            InlineKeyboardButton("👤 1 Usuário - 15 Dias", callback_data='usuario_1_15'),
            InlineKeyboardButton("R$10,00", callback_data='usuario_1_15')
        ],
        [
            InlineKeyboardButton("👤 1 Usuário - 30 Dias", callback_data='usuario_1_30'),
            InlineKeyboardButton("R$17,00", callback_data='usuario_1_30')
        ],
        [
            InlineKeyboardButton("👤 1 Usuário - 40 Dias", callback_data='usuario_1_40'),
            InlineKeyboardButton("R$20,00", callback_data='usuario_1_40')
        ],
        [
            InlineKeyboardButton("👥 2 Usuários - 30 Dias", callback_data='usuario_2_30'),
            InlineKeyboardButton("R$27,00", callback_data='usuario_2_30')
        ],
        [
            InlineKeyboardButton("👥 3 Usuários - 30 Dias", callback_data='usuario_3_30'),
            InlineKeyboardButton("R$37,00", callback_data='usuario_3_30')
        ],
        [
            InlineKeyboardButton("👥 4 Usuários - 30 Dias", callback_data='usuario_4_30'),
            InlineKeyboardButton("R$47,00", callback_data='usuario_4_30')
        ],
        [
            InlineKeyboardButton("💰 Seja um Revendedor", callback_data='revenda_menu')
        ],
        [
            InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

# Função para o sub-menu de revenda
async def revenda_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Exibindo o menu de revenda")

    # Mensagem promocional com destaques
    message = (
        "<b>📈 Amplie seus Lucros:</b>\n\n"
        "🔹 <b>Oportunidade Única</b> | <b>Ferramentas Avançadas</b>\n"
        "🔹 <b>Painel Completo</b> | <b>Suporte Dedicado</b>\n\n"
        "🚀 Escolha seu plano de revenda:"
    )

    # Botões dos planos de revenda organizados em duas colunas para clareza
    keyboard = [
        [
            InlineKeyboardButton("💼 Revenda Start - 10 Clientes", callback_data='revenda_start'),
            InlineKeyboardButton("R$30,00", callback_data='revenda_start')
        ],
        [
            InlineKeyboardButton("💼 Revenda Básica - 20 Clientes", callback_data='revenda_basica'),
            InlineKeyboardButton("R$52,50", callback_data='revenda_basica')
        ],
        [
            InlineKeyboardButton("💼 Revenda Intermediária - 50 Clientes", callback_data='revenda_intermediaria'),
            InlineKeyboardButton("R$90,00", callback_data='revenda_intermediaria')
        ],
        [
            InlineKeyboardButton("💼 Revenda Avançada - 100 Clientes", callback_data='revenda_avancada'),
            InlineKeyboardButton("R$135,00", callback_data='revenda_avancada')
        ],
        [
            InlineKeyboardButton("💼 Revenda Premium - 150 Clientes", callback_data='revenda_premium'),
            InlineKeyboardButton("R$180,00", callback_data='revenda_premium')
        ],
        [
            InlineKeyboardButton("💼 Revenda Elite - 200 Clientes", callback_data='revenda_elite'),
            InlineKeyboardButton("R$225,00", callback_data='revenda_elite')
        ],
        [
            InlineKeyboardButton("📦 Materiais de Venda", url='https://t.me/BANNERS_NET_ILIMITADA')
        ],
        [
            InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

# Função para exibir o menu de FAQ
async def faq_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Exibindo o menu de FAQ")

    message = (
        "<b>❓ Dúvidas Frequentes</b>\n\n"
        "Estamos aqui para ajudar! 🤖💬\n\n"
        "Selecione a plataforma para mais informações:"
    )

    # Botões para seleção de FAQ organizados de forma equilibrada
    keyboard = [
        [
            InlineKeyboardButton("🤖 Android", callback_data='faq_android'),
            InlineKeyboardButton("🍏 iOS", callback_data='faq_ios')
        ],
        [
            InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Envia a mensagem com as opções
    if update.callback_query:
        await update.callback_query.message.edit_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

# Função para lidar com os botões pressionados
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.debug(f"Callback data received: {query.data}")

    if query.data == 'comprar_ios':
        logger.debug("Exibindo menu de Internet Ilimitada")
        await comprar_ios_menu(update, context)
    elif query.data in ['usuario_1_15', 'usuario_1_30', 'usuario_1_40', 'usuario_2_30', 'usuario_3_30', 'usuario_4_30']:
        logger.debug(f"Processando pagamento para plano de usuário: {query.data}")
        await process_payment(update, context, plano_selecionado=query.data)
    elif query.data == 'revenda_menu':
        logger.debug("Exibindo menu de revenda")
        await revenda_menu(update, context)
    elif query.data in ['revenda_start', 'revenda_basica', 'revenda_intermediaria', 'revenda_avancada', 'revenda_premium', 'revenda_elite']:
        logger.debug(f"Processando pagamento para plano de revenda: {query.data}")
        await process_payment(update, context, plano_selecionado=query.data)
    elif query.data.startswith('confirmar_'):
        logger.debug(f"Confirmando pagamento para {query.data}")
        await confirm_payment(update, context)
    elif query.data == 'afiliado':
        logger.debug("Exibindo painel de afiliados")
        await affiliate_dashboard(update, context)
    elif query.data == 'start':
        logger.debug("Retornando ao menu principal")
        await start_command(update, context)
    elif query.data == 'remarketing_offer':
        logger.debug("Processando oferta de remarketing")
        from remarketing_handler import handle_remarketing_offer
        await handle_remarketing_offer(update, context)
    elif query.data == 'teste_gratis':
        logger.debug("Lidando com solicitação de teste grátis")
        await test_service.handle_test_request(update, context)
    elif query.data == 'faq_menu':
        logger.debug("Acessando sub-menu de FAQ")
        await faq_menu(update, context)
    elif query.data == 'faq_android':
        logger.debug("Acessando FAQ Android")
        await faq_android_start(update, context)
    elif query.data == 'faq_ios':
        logger.debug("Acessando FAQ iOS")
        await faq_ios_start(update, context)
    else:
        logger.warning(f"Dados de callback desconhecidos: {query.data}")
