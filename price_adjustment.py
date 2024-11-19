#price_adjustment.py
import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

# Arquivo para armazenar os ajustes de preço
PRICE_ADJUSTMENT_FILE = 'price_adjustment.json'

def load_price_adjustment():
    if os.path.exists(PRICE_ADJUSTMENT_FILE):
        with open(PRICE_ADJUSTMENT_FILE, 'r') as file:
            try:
                data = json.load(file)
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def save_price_adjustment(data):
    with open(PRICE_ADJUSTMENT_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def delete_price_adjustment():
    """Remove o ajuste de preço ativo."""
    if os.path.exists(PRICE_ADJUSTMENT_FILE):
        os.remove(PRICE_ADJUSTMENT_FILE)

def is_adjustment_valid():
    data = load_price_adjustment()
    if data:
        end_date_str = data.get('end_date')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
            if datetime.now() <= end_date:
                return True
    return False

def get_current_adjustment():
    if is_adjustment_valid():
        data = load_price_adjustment()
        operator = data.get('operator')
        percentage = data.get('percentage')
        return operator, percentage
    else:
        return None, 0

async def price_adjustment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Você não tem permissão para usar este comando.")
        return

    args = context.args

    # Se nenhum argumento for fornecido, mostra o ajuste atual
    if not args:
        if is_adjustment_valid():
            data = load_price_adjustment()
            operator = data.get('operator')
            percentage = data.get('percentage')
            end_date_str = data.get('end_date')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
            remaining_days = (end_date - datetime.now()).days + 1  # Adiciona 1 para incluir o dia atual
            await update.message.reply_text(
                f"Ajuste de preço atual: {operator}{percentage}% válido por mais {remaining_days} dia(s)."
            )
        else:
            await update.message.reply_text("Não há nenhum ajuste de preço ativo no momento.")
        return

    # Comando para desativar o ajuste
    if args[0].lower() == 'desativar':
        delete_price_adjustment()
        await update.message.reply_text("Ajuste de preço desativado com sucesso.")
        return

    # Verifica se os argumentos são válidos
    if len(args) != 2:
        await update.message.reply_text(
            "Uso inválido do comando. Use /preco [+|-]<percentual> <duração_em_dias>\n"
            "Exemplo: /preco -15 30"
        )
        return

    operator_percentage = args[0]
    duration_str = args[1]

    operator = operator_percentage[0]
    if operator not in ['+', '-']:
        await update.message.reply_text("Operador inválido. Use '+' para aumento ou '-' para desconto.")
        return

    try:
        percentage = int(operator_percentage[1:])
        if percentage <= 0 or percentage > 100:
            await update.message.reply_text("O percentual deve ser um número inteiro entre 1 e 100.")
            return
    except ValueError:
        await update.message.reply_text("Percentual inválido. Use um número inteiro.")
        return

    try:
        duration = int(duration_str)
        if duration < 1 or duration > 365:
            await update.message.reply_text("A duração deve ser entre 1 e 365 dias.")
            return
    except ValueError:
        await update.message.reply_text("Duração inválida. Use um número inteiro.")
        return

    end_date = datetime.now() + timedelta(days=duration)
    data = {
        'operator': operator,
        'percentage': percentage,
        'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S')
    }
    save_price_adjustment(data)

    await update.message.reply_text(
        f"Ajuste de preço configurado: {operator}{percentage}% válido por {duration} dia(s)."
    )

def adjust_price(original_price):
    operator, percentage = get_current_adjustment()
    if operator:
        if operator == '+':
            adjusted_price = original_price * (1 + percentage / 100)
        elif operator == '-':
            adjusted_price = original_price * (1 - percentage / 100)
        else:
            adjusted_price = original_price
        return round(adjusted_price, 2)
    else:
        return original_price

def setup_price_adjustment_handlers(application):
    application.add_handler(CommandHandler('preco', price_adjustment_command))
