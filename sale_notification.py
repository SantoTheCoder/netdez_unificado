#SALE_NOTIFICATION.PY

import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes
from config import (
    API_KEY, BOT_LINK_DESTINO, TELEGRAM_CHAT_ID, TELEGRAM_CHAT_USERNAME, ADMIN_ID,
    TELEGRAM_SALES_GROUP_ID as SALES_CHAT_ID,
    TELEGRAM_CONTROL_CHANNEL_ID as CONTROL_CHAT_ID,
    MIN_DAILY_SALES, MAX_DAILY_SALES, BASE_SALES_INTERVAL, PEAK_HOURS,
    SIMULATE_SALES_AUTOMATICALLY
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Configuração do Logger com cores
import sys
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configuração de formatação com cores
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    }
)

# Configurando o console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Estado da simulação
simulation_state = 'inactive'  # Possíveis estados: 'inactive', 'active'

# Lista de planos individuais com suas respectivas informações e probabilidades
USER_PLANS = [
    {"name": "Plano 1 Pessoa - 30 Dias", "price": 17.0, "validity_days": 30, "user_limit": 1, "probability": 60},
    {"name": "Plano 1 Pessoa - 40 Dias", "price": 20.0, "validity_days": 40, "user_limit": 1, "probability": 20},
    {"name": "Plano 1 Pessoa - 15 Dias", "price": 10.0, "validity_days": 15, "user_limit": 1, "probability": 7},
    {"name": "Plano 2 Pessoas - 30 Dias", "price": 27.0, "validity_days": 30, "user_limit": 2, "probability": 10},
    {"name": "Plano 3 Pessoas - 30 Dias", "price": 37.0, "validity_days": 30, "user_limit": 3, "probability": 2},
    {"name": "Plano 4 Pessoas - 30 Dias", "price": 47.0, "validity_days": 30, "user_limit": 4, "probability": 1},
]

# Lista de planos de revenda com probabilidades
RESELLER_PLANS = [
    {"name": "Revenda Start - 10 Pessoas", "price": 30.0, "validity_days": 30, "user_limit": 10, "probability": 60},
    {"name": "Revenda Básica - 20 Pessoas", "price": 52.5, "validity_days": 30, "user_limit": 20, "probability": 20},
    {"name": "Revenda Média - 50 Pessoas", "price": 90.0, "validity_days": 30, "user_limit": 50, "probability": 13},
    {"name": "Revenda Master - 100 Pessoas", "price": 135.0, "validity_days": 30, "user_limit": 100, "probability": 5},
    {"name": "Revenda Top - 150 Pessoas", "price": 180.0, "validity_days": 30, "user_limit": 150, "probability": 1},
    {"name": "Revenda Elite - 200 Pessoas", "price": 225.0, "validity_days": 30, "user_limit": 200, "probability": 1},
]

# Função para obter ID e nome do cliente dos arquivos (apenas para simulação)
def get_customer_info():
    try:
        with open('customer_ids.txt', 'r+', encoding='utf-8') as id_file, open('customer_names.txt', 'r+', encoding='utf-8') as name_file:
            customer_ids = id_file.readlines()
            customer_names = name_file.readlines()
            if not customer_ids or not customer_names:
                return None, None

            index = random.randint(0, len(customer_names) - 1)  # Seleciona um índice aleatório
            customer_id = customer_ids[index].strip()
            customer_name = customer_names[index].strip().split()[0]
            
            # Remove o nome e ID selecionados para evitar repetição no mesmo ciclo
            customer_ids.pop(index)
            customer_names.pop(index)
            
            id_file.seek(0)
            name_file.seek(0)
            id_file.writelines(customer_ids)
            name_file.writelines(customer_names)
            id_file.truncate()
            name_file.truncate()

        return customer_id, customer_name
    except FileNotFoundError:
        return None, None

# Função para gerar um ID de compra realista no intervalo fornecido (para simulação)
def generate_purchase_id():
    return str(random.randint(92783494879, 93106071228))

# Função para escolher plano com base nas probabilidades
def choose_plan():
    category_choice = random.choices(
        ["user", "reseller"],
        weights=[90, 10],  # Usuário: 90%, Revenda: 10%
        k=1
    )[0]
    logger.debug(f"Categoria escolhida: {category_choice}")

    plans = USER_PLANS if category_choice == "user" else RESELLER_PLANS
    chosen_plan = random.choices(plans, weights=[p['probability'] for p in plans], k=1)[0]
    logger.debug(f"Plano escolhido: {chosen_plan['name']} com probabilidade {chosen_plan['probability']}%")
    return chosen_plan

# Função para enviar notificação de venda com suporte a `destination_chat_id`
async def send_sale_notification(customer_name, service_name, customer_id, purchase_id, destination_chat_id=None):
    bot = Bot(token=API_KEY)
    destination_chat_id = destination_chat_id or SALES_CHAT_ID
    
    # Extrai apenas a parte única do ID da Compra
    purchase_id_unique = purchase_id.split('-')[1] if '-' in purchase_id else purchase_id

    message = (
        f"<b>💰️ {customer_name} fez uma nova compra!</b>\n\n"
        f"<b>Serviço:</b> {service_name}\n"
        f"<b>ID do Cliente:</b> {customer_id}\n"
        f"<b>ID da Compra:</b> {purchase_id_unique}\n\n"
        "⭐️ Cansou de usar VPN de servidores que vivem caindo? Vem para o melhor servidor SSH do Brasil, clica no botão abaixo para comprar o seu login vip de 30 dias. 👇️👇️👇️"
    )

    keyboard = [[InlineKeyboardButton("🛍️ COMPRAR LOGIN VIP", url=BOT_LINK_DESTINO)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await bot.send_message(chat_id=destination_chat_id, text=message, reply_markup=reply_markup, parse_mode='HTML')
        logger.info(f"Notificação de venda enviada para ID de compra: {purchase_id_unique} no canal ID: {destination_chat_id}")
    except Exception as e:
        logger.error(f"Falha ao enviar notificação de venda para ID {destination_chat_id}: {e}")
        try:
            await bot.send_message(chat_id=TELEGRAM_CHAT_USERNAME, text=message, reply_markup=reply_markup, parse_mode='HTML')
            logger.info(f"Notificação de venda enviada para ID de compra: {purchase_id_unique} no canal username: {TELEGRAM_CHAT_USERNAME}")
        except Exception as e:
            logger.error(f"Falha ao enviar notificação de venda para username {TELEGRAM_CHAT_USERNAME}: {e}")

# Função para processar uma venda real com dados reais
async def process_real_sale(customer_name, service_name, customer_id, purchase_id, sale_amount, user_limit, validity_days, context, destination_chat_id=CONTROL_CHAT_ID):
    await send_sale_notification(
        customer_name=customer_name,
        service_name=service_name,
        customer_id=customer_id,
        purchase_id=purchase_id,
        destination_chat_id=destination_chat_id
    )

    from payment_handlers import register_sale

    register_sale(
        chat_id=int(customer_id),
        sale_type='usuario' if user_limit == 1 else 'revenda',
        amount=sale_amount,
        buyer_name=customer_name
    )

# Comando /vendarealizada para simular uma venda manualmente
async def simulate_real_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    customer_id, customer_name = get_customer_info()
    if not customer_id or not customer_name:
        await update.message.reply_text("IDs ou nomes de cliente esgotados para simulação.")
        return

    purchase_id = generate_purchase_id()
    selected_plan = choose_plan()
    service_name = selected_plan["name"]
    sale_amount = selected_plan["price"]
    user_limit = selected_plan["user_limit"]
    validity_days = selected_plan["validity_days"]

    logger.info(f"Plano selecionado: {service_name} com validade de {validity_days} dias e limite de {user_limit} usuário(s).")

    await send_sale_notification(
        customer_name=customer_name,
        service_name=service_name,
        customer_id=customer_id,
        purchase_id=purchase_id,
        destination_chat_id=SALES_CHAT_ID
    )

    await update.message.reply_text(f"Venda simulada para {customer_name} com ID de compra {purchase_id}.")

# Função para simular vendas automáticas com distribuição uniforme ao longo de 24 horas
async def simulate_sales_task(application):
    global simulation_state  # Use global to modify the variable within this function
    if not SIMULATE_SALES_AUTOMATICALLY or simulation_state == 'active':  # Prevent re-entry if already active
        logger.info("Simulação de vendas automáticas está desativada ou já ativa.")
        return

    simulation_state = 'active'  # Set the state to active when the simulation starts
    daily_sales = random.randint(MIN_DAILY_SALES, MAX_DAILY_SALES)
    logger.info(f"Serão simuladas {daily_sales} vendas no próximo ciclo de 24 horas.")

    now = datetime.now()
    start_time = now
    end_time = start_time + timedelta(hours=24)
    total_duration_seconds = (end_time - start_time).total_seconds()
    interval_seconds = total_duration_seconds / daily_sales

    sale_times = []
    for i in range(daily_sales):
        # Calcula o horário previsto para a venda
        scheduled_time = start_time + timedelta(seconds=i * interval_seconds)
        # Adiciona um pequeno jitter aleatório para evitar vendas exatamente no mesmo intervalo
        jitter_seconds = random.uniform(-interval_seconds * 0.1, interval_seconds * 0.1)
        scheduled_time += timedelta(seconds=jitter_seconds)

        # Garantir que o horário da venda esteja dentro dos limites do ciclo de 24 horas
        if scheduled_time < start_time:
            scheduled_time = start_time
        elif scheduled_time > end_time:
            scheduled_time = end_time

        sale_times.append(scheduled_time)

    # Ordena os horários das vendas
    sale_times.sort()

    # Agenda as vendas
    for idx, sale_time in enumerate(sale_times):
        # Ajusta a probabilidade com base no horário e usa a configuração de horários de pico
        current_hour = sale_time.hour
        is_peak_hour = False
        for period, info in PEAK_HOURS.items():
            start = info["start"]
            end = info["end"]
            probability = info["probability"]

            if start <= end:
                in_period = start <= current_hour < end
            else:
                in_period = current_hour >= start or current_hour < end

            if in_period:
                if random.random() <= probability:
                    is_peak_hour = True
                    logger.debug(f"Horário de pico ({period}): {current_hour}h, probabilidade aplicada: {probability}")
                else:
                    # Adiciona um atraso adicional se fora do horário de pico
                    sale_time += timedelta(minutes=random.randint(10, 30))
                    logger.debug(f"Fora do horário de pico ({period}), ajustando próximo horário para {sale_time}")
                break

        # Log detalhado do cálculo
        logger.info(f"Agendando venda simulada #{idx + 1}")
        logger.debug(f"Horário da venda agendado para: {sale_time}")

        # Agenda a venda
        application.job_queue.run_once(
            execute_simulated_sale,
            when=(sale_time - datetime.now()).total_seconds()
        )

    # Reset the simulation state after 24 hours
    asyncio.create_task(reset_simulation_state(application))

# Função que redefine o estado da simulação e reinicia o ciclo
async def reset_simulation_state(application):
    await asyncio.sleep(86400)  # Aguarda 24 horas
    global simulation_state
    simulation_state = 'inactive'  # Define o estado de volta para inativo
    logger.info("Simulação de vendas redefinida para inativa.")
    # Reinicia a simulação chamando simulate_sales_task
    await simulate_sales_task(application)

# Função que executa a venda simulada
async def execute_simulated_sale(context: ContextTypes.DEFAULT_TYPE):
    customer_id, customer_name = get_customer_info()
    if not customer_id or not customer_name:
        logger.warning("IDs ou nomes de cliente esgotados para simulação.")
        return

    purchase_id = generate_purchase_id()
    selected_plan = choose_plan()
    service_name = selected_plan["name"]
    sale_amount = selected_plan["price"]
    user_limit = selected_plan["user_limit"]
    validity_days = selected_plan["validity_days"]

    logger.info(f"Simulando venda: {service_name} para {customer_name} (ID: {customer_id}).")

    await send_sale_notification(
        customer_name=customer_name,
        service_name=service_name,
        customer_id=customer_id,
        purchase_id=purchase_id,
        destination_chat_id=SALES_CHAT_ID
    )

# Função para iniciar a tarefa de simulação de vendas
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

def start_simulation_task(scheduler, application):
    if not SIMULATE_SALES_AUTOMATICALLY:
        logger.info("Sistema de simulação de vendas automáticas está desativado.")
        return

    initial_delay = 30  # segundos
    start_time = datetime.now() + timedelta(seconds=initial_delay)

    async def run_simulate_sales_task():
        # Usa o loop de eventos do asyncio para garantir que a função seja executada corretamente
        loop = asyncio.get_running_loop()
        loop.create_task(simulate_sales_task(application))

    # Agenda a primeira execução após 30 segundos
    scheduler.add_job(
        run_simulate_sales_task,
        trigger=DateTrigger(run_date=start_time),
        id='simulate_sales_first_cycle',
        replace_existing=True
    )
    logger.info(f"Primeiro ciclo de vendas agendado para iniciar em {start_time}.")

    # Agenda as execuções subsequentes a cada 24 horas
    scheduler.add_job(
        run_simulate_sales_task,
        trigger=IntervalTrigger(hours=24, start_date=start_time),
        id='simulate_sales_daily',
        replace_existing=True
    )
    logger.info(f"Ciclos de vendas agendados para ocorrer a cada 24 horas a partir de {start_time}.")

def setup_admin_handlers(application):
    application.add_handler(CommandHandler("vendarealizada", simulate_real_sale))
