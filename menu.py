# MENU.PY
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from payment_handlers import process_payment, confirm_payment
from affiliate_system import affiliate_dashboard
import test_service

logger = logging.getLogger(__name__)

# Função para criar o menu principal
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Exibindo o menu principal")

    # Mensagem de boas-vindas atualizada
    message = (
        "✨ <b>Bem-vindo ao NetDez!</b> 🚀\n\n"
        "🌐 Internet Ilimitada com qualidade. Escolha uma opção abaixo para começar:"
    )

    # Botões do menu principal organizados conforme a descrição
    keyboard = [
        [
            InlineKeyboardButton("🚀 Internet Ilimitada", callback_data='comprar_ios'),
            InlineKeyboardButton("🍏 iOS Ilimitado", url='https://t.me/netdez_ios_bot')
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
            InlineKeyboardButton("❓ FAQ / Dúvidas Frequentes", callback_data='faq')
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

    # Mensagem persuasiva
    message = (
        "<b>🔍 Escolha o Melhor Plano para Você e Navegue Ilimitado:</b>\n"
        "Selecione um dos planos abaixo:"
    )

    # Botões dos planos de usuários com variações de preço e duração
    keyboard = [
        [InlineKeyboardButton("👤 1 Usuário - 15 Dias - R$10,00", callback_data='usuario_1_15')],
        [InlineKeyboardButton("👤 1 Usuário - 30 Dias - R$17,00", callback_data='usuario_1_30')],
        [InlineKeyboardButton("👤 1 Usuário - 40 Dias - R$20,00", callback_data='usuario_1_40')],
        [InlineKeyboardButton("👥 2 Usuários - 30 Dias - R$27,00", callback_data='usuario_2_30')],
        [InlineKeyboardButton("👥 3 Usuários - 30 Dias - R$37,00", callback_data='usuario_3_30')],
        [InlineKeyboardButton("👥 4 Usuários - 30 Dias - R$47,00", callback_data='usuario_4_30')],
        [InlineKeyboardButton("💰 Seja um Revendedor", callback_data='revenda_menu')],
        [InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')]
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

    # Mensagem promocional
    message = (
        "<b>📈 Invista na Revenda e Aumente seus Lucros com NetDez:</b>\n"
        "Escolha um dos planos de revenda abaixo:"
    )

    # Botões dos novos planos de revenda
    keyboard = [
        [InlineKeyboardButton("💼 Revenda Start - 10 Clientes - R$40,00", callback_data='revenda_start')],
        [InlineKeyboardButton("💼 Revenda Básica - 20 Clientes - R$70,00", callback_data='revenda_basica')],
        [InlineKeyboardButton("💼 Revenda Intermediária - 50 Clientes - R$120,00", callback_data='revenda_intermediaria')],
        [InlineKeyboardButton("💼 Revenda Avançada - 100 Clientes - R$180,00", callback_data='revenda_avancada')],
        [InlineKeyboardButton("💼 Revenda Premium - 150 Clientes - R$240,00", callback_data='revenda_premium')],
        [InlineKeyboardButton("💼 Revenda Elite - 200 Clientes - R$300,00", callback_data='revenda_elite')],
        [InlineKeyboardButton("📦 Materiais de Venda", url='https://t.me/BANNERS_NET_ILIMITADA')],
        [InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
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
    elif query.data == 'faq':
        logger.debug("Acessando FAQ")
        from faq import faq_start
        await faq_start(update, context)
