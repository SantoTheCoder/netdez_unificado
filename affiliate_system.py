#affiliate_system.py
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler
from database import get_db_connection
from config import BOT_NAME, SUPPORT_CONTACT

logger = logging.getLogger(__name__)

def create_affiliate_link(user_id):
    return f"https://t.me/{BOT_NAME.lstrip('@')}?start={user_id}"

async def record_affiliate_purchase(affiliate_id, referred_user_id, context):
    conn = get_db_connection()
    if conn is None:
        logger.error("Erro ao conectar ao banco de dados ao tentar registrar a compra do afiliado.")
        return

    cursor = conn.cursor()
    
    try:
        logger.info(f"Registrando compra para o afiliado {affiliate_id} referindo o usuário {referred_user_id}")
        
        cursor.execute('''
        INSERT INTO affiliates (affiliate_id, referred_user_id, timestamp)
        VALUES (?, ?, ?)
        ''', (affiliate_id, referred_user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        logger.info("Registro de compra do afiliado bem-sucedido.")
    except Exception as e:
        logger.error(f"Erro ao registrar a compra do afiliado: {e}")
    finally:
        conn.close()

    # Conceder o vale usuário ao afiliado
    await grant_user_voucher(affiliate_id, context)
    
    logger.info(f"Vale usuário de 30 dias concedido ao afiliado {affiliate_id}")

def get_affiliate_stats(affiliate_id):
    conn = get_db_connection()
    if conn is None:
        logger.error("Erro ao conectar ao banco de dados ao tentar obter as estatísticas do afiliado.")
        return {
            'total_referred': 0,
            'last_referred_user': 'n/a',
            'last_referred_time': 'Nenhuma ainda'
        }
    
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT COUNT(*) as total_referred, MAX(timestamp) as last_referred_time, MAX(referred_user_id) as last_referred_user
    FROM affiliates WHERE affiliate_id = ?
    ''', (affiliate_id,))
    
    stats = cursor.fetchone()
    conn.close()
    
    return {
        'total_referred': stats['total_referred'],
        'last_referred_user': stats['last_referred_user'] or 'n/a',
        'last_referred_time': stats['last_referred_time'] or 'Nenhuma ainda'
    }

async def affiliate_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = create_affiliate_link(user_id)
    stats = get_affiliate_stats(user_id)
    
    # Mensagem atualizada do painel de afiliação
    message = (
        "<b>🎉 Ganhe Mais com Nossas Indicações! 🎉</b>\n\n"
        f"✅ <b>Total de Indicações:</b> <code>{stats['total_referred']}</code>\n"
        f"🔎 <b>Última Indicação:</b> <code>{stats['last_referred_user']}</code>\n"
        f"⏳ <b>Horário da Última Indicação:</b> <code>{stats['last_referred_time']}</code>\n\n"
        f"🔗 <b>Seu Link Exclusivo:</b> <a href='{link}'>{link}</a>\n\n"
        "<b>🌟 Como funciona?</b>\n"
        "- <b>Recomendou e o amigo comprou?</b> Ganha <b>30 dias grátis</b>! 📅✨\n"
        "- <b>5 Indicações completadas?</b> Ganhe um <b>painel de revenda gratuito</b> para começar a revender e aumentar seus ganhos! 💼💸\n\n"
        "🚀 <b>Compartilhe seu link e comece a acumular recompensas agora mesmo!</b>"
    )
    
    buttons = [
        [InlineKeyboardButton("⬅️ Voltar ao Menu Principal", callback_data='start')]  # Alterado para callback_data='start'
    ]
    
    if update.message:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    elif update.callback_query:
        await update.callback_query.message.edit_text(message, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

def setup_affiliate_handlers(application):
    application.add_handler(CommandHandler("affiliate_dashboard", affiliate_dashboard))

async def handle_affiliate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referrer_id = context.args[0] if context.args else None

    if referrer_id:
        logger.info(f"Usuário {user_id} iniciou o bot através do link de afiliação de {referrer_id}")
        context.user_data['referrer_id'] = referrer_id  # Armazena o ID do afiliado

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                SELECT COUNT(*) FROM affiliates WHERE referred_user_id = ?
                ''', (user_id,))
                already_registered = cursor.fetchone()[0]
                
                if not already_registered:
                    # Registra a indicação no banco de dados
                    cursor.execute('''
                    INSERT INTO affiliates (affiliate_id, referred_user_id, timestamp)
                    VALUES (?, ?, ?)
                    ''', (referrer_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    
                    conn.commit()
                    logger.info(f"Indicação do usuário {user_id} pelo afiliado {referrer_id} registrada com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao verificar o usuário no banco de dados: {e}")
            finally:
                conn.close()

        # Mensagem de boas-vindas para o novo usuário
        user_message = f"🎉 Bem-vindo! Você foi indicado por {referrer_id}. Aproveite nossos serviços!"
        await update.message.reply_text(user_message)

        # Notificação ao dono do link de indicação (afiliado)
        referrer_message = (
            f"🚀 <b>Parabéns!</b> Um novo usuário iniciou o bot com seu link de indicação!\n\n"
            f"<b>ID do Usuário Indicado:</b> {user_id}\n\n"
            "Continue compartilhando para acumular mais recompensas!"
        )
        await notify_affiliate(referrer_id, referrer_message, context)
        
    else:
        logger.info(f"Usuário {user_id} iniciou o bot sem link de afiliação.")

async def grant_user_voucher(affiliate_id, context):
    voucher_message = (
        "🎉 <b>Parabéns!</b> 🎉\n\n"
        "Você recebeu um <b>Vale Usuário</b> de 30 dias pelo sucesso em indicar um novo cliente! 🏆\n\n"
        f"Para resgatar seu usuário, por favor entre em contato com nosso suporte.\n\n"
        f"📞 <b>Suporte:</b> {SUPPORT_CONTACT}\n\n"
        "🕒 <b>Validade do Vale:</b> 30 dias a partir da data de recebimento.\n\n"
        "⚠️ <b>Instruções:</b>\n"
        "1. Envie esta mensagem ao nosso suporte.\n"
        "2. Aguarde o atendimento para receber seu usuário.\n\n"
        "Obrigado por confiar em nossos serviços! 🙌"
    )
    
    logger.info(f"Enviando vale usuário para o afiliado {affiliate_id}")
    return await notify_affiliate(affiliate_id, voucher_message, context)

async def notify_affiliate(affiliate_id, message, context):
    try:
        await context.bot.send_message(chat_id=affiliate_id, text=message, parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem ao afiliado {affiliate_id}: {e}")
        return False
