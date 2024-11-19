# main.py
import logging
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from config import API_KEY
from resellers import create_reseller_command
from users import create_user_command, create_test_user_command
from menu import start_command, button_handler, revenda_menu
from affiliate_system import setup_affiliate_handlers, handle_affiliate_start
from broadcast import setup_broadcast_handlers
from database import get_db_connection
from relatorio import generate_report
from notificacoes_vencimento import verificar_vencimentos_periodicamente
from remarketing_handler import setup_remarketing_handlers, start_remarketing_task
from payment_handlers import setup_payment_handlers
import test_service  # Importando o módulo de teste gratuito
from test_service import setup_test_service_handlers  # Importando o setup para handlers de teste
from price_adjustment import price_adjustment_command  # Importa a função de comando de ajuste de preço correta
from faq import faq_start, setup_faq_handlers  # Importando o FAQ para o botão no menu principal e setup de handlers
from sale_notification import setup_admin_handlers, start_simulation_task  # Importa o setup para o comando de simulação de venda

# Configuração de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Função para lidar com o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Registra o usuário na tabela 'users'
    chat_id = update.effective_user.id
    username = update.effective_user.username

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO users (chat_id, username)
    VALUES (?, ?)
    ''', (chat_id, username))

    conn.commit()
    conn.close()
    logger.info(f"Usuário {chat_id} ({username}) registrado no banco de dados.")

    # Verifica se o usuário iniciou o bot com um link de afiliado
    if context.args:
        await handle_affiliate_start(update, context)
    await start_command(update, context)

# Função para resetar o bot e reiniciar tarefas
def reset_bot(scheduler, application):
    logger.info("Resetando o bot e reiniciando tarefas...")

    # Remove todos os jobs, exceto o próprio reset_bot
    for job in scheduler.get_jobs():
        if job.id != 'reset_bot':
            scheduler.remove_job(job.id)

    # Reinicia as tarefas necessárias
    # Reagendar tarefas como start_simulation_task, start_remarketing_task, etc.

    start_simulation_task(scheduler, application)
    start_remarketing_task(scheduler, application)

    # Verificação de vencimentos periodicamente (agendamento)
    scheduler.add_job(
        lambda: application.create_task(verificar_vencimentos_periodicamente()),
        trigger=IntervalTrigger(hours=24),
        timezone=pytz.UTC,
        id='verificar_vencimentos',
        replace_existing=True
    )
    logger.info("Tarefa de verificação de vencimentos agendada para rodar a cada 24 horas.")

    # Reset mensal dos registros de testes gratuitos
    scheduler.add_job(
        test_service.reset_monthly,
        trigger=IntervalTrigger(days=1),
        timezone=pytz.UTC,
        id='reset_monthly_tests',
        replace_existing=True
    )
    logger.info("Tarefa de reset mensal dos registros de testes agendada para rodar diariamente.")

    logger.info("Reset concluído. Tarefas reiniciadas.")

# Função principal que configura e roda o bot
def main():
    logger.info("Configurando a aplicação...")
    # Criação da aplicação do bot
    application = Application.builder().token(API_KEY).build()

    # Criação do scheduler para tarefas periódicas com o fuso horário configurado corretamente
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    scheduler.start()

    # Configurando os handlers do Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("createreseller", create_reseller_command))
    application.add_handler(CommandHandler("createuser", create_user_command))
    application.add_handler(CommandHandler("createtest", create_test_user_command))
    application.add_handler(CommandHandler("relatorio", generate_report))
    application.add_handler(CommandHandler("preco", price_adjustment_command))  # Comando de ajuste de preço corrigido

    # Configurando o comando de simulação de venda para administradores
    setup_admin_handlers(application)  # Adiciona o handler do comando /vendarealizada para admins

    # Configurando os handlers de pagamento
    setup_payment_handlers(application)

    # Configurando os handlers de remarketing
    setup_remarketing_handlers(application)

    # Configurando o sistema de afiliação
    setup_affiliate_handlers(application)

    # Configurando o sistema de broadcast
    setup_broadcast_handlers(application)

    # Configurando os handlers para confirmação do teste gratuito
    setup_test_service_handlers(application)

    # Configurando o FAQ handlers
    setup_faq_handlers(application)  # Configura os handlers de FAQ incluindo botão do menu e navegação

    # Handlers para botões inline (callback queries) específicos
    application.add_handler(CallbackQueryHandler(revenda_menu, pattern='^revenda_menu$'))
    application.add_handler(CallbackQueryHandler(start_command, pattern='^start$'))  # Voltar ao início

    # Handler geral para botões inline - deve ser adicionado por último
    application.add_handler(CallbackQueryHandler(button_handler))  # Handler principal para botões inline

    # Iniciando a tarefa de remarketing com o agendamento configurado
    start_remarketing_task(scheduler, application)

    # Verificação de vencimentos periodicamente (agendamento)
    scheduler.add_job(
        lambda: application.create_task(verificar_vencimentos_periodicamente()),
        trigger=IntervalTrigger(hours=24),
        timezone=pytz.UTC,
        id='verificar_vencimentos',
        replace_existing=True
    )
    logger.info("Tarefa de verificação de vencimentos agendada para rodar a cada 24 horas.")

    # Reset mensal dos registros de testes gratuitos
    scheduler.add_job(
        test_service.reset_monthly,
        trigger=IntervalTrigger(days=1),
        timezone=pytz.UTC,
        id='reset_monthly_tests',
        replace_existing=True
    )
    logger.info("Tarefa de reset mensal dos registros de testes agendada para rodar diariamente.")

    # Inicia a simulação de vendas automáticas
    start_simulation_task(scheduler, application)

    # Agendar o reset_bot para executar 30 segundos após o início e depois a cada intervalo definido
    FIRST_RESET_DELAY_SECONDS = 30  # Tempo após o início para o primeiro reset
    RESET_INTERVAL_SECONDS = 86400  # Intervalo entre resets em segundos (1 hora)

    scheduler.add_job(
        reset_bot,
        trigger=IntervalTrigger(seconds=RESET_INTERVAL_SECONDS, start_date=datetime.now() + timedelta(seconds=FIRST_RESET_DELAY_SECONDS)),
        args=[scheduler, application],
        id='reset_bot',
        replace_existing=True
    )
    logger.info(f"Reset do bot agendado para {FIRST_RESET_DELAY_SECONDS} segundos após o início e depois a cada {RESET_INTERVAL_SECONDS} segundos.")

    logger.info("Iniciando o bot com polling...")
    # Rodar o bot com polling
    application.run_polling()

if __name__ == '__main__':
    main()
