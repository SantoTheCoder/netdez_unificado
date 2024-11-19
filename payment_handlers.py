# payment_handlers.py 
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, CallbackQueryHandler
from mercadopago import gerar_qr_code_mercado_pago, mp
import logging
import asyncio
import base64
from utils import notify_telegram
from datetime import datetime, timedelta
from sales import create_user_for_sale
from resellers import create_reseller
import json
import os
import requests
from config import (
    IOS_API_KEY, PAYER_EMAIL, PAYER_FIRST_NAME, PAYER_LAST_NAME,
    PAYER_IDENTIFICATION_TYPE, PAYER_IDENTIFICATION_NUMBER, URL_PAINEL_API,
    TELEGRAM_SALES_GROUP_ID, TELEGRAM_CONTROL_CHANNEL_ID  # Import new variables
)
from affiliate_system import record_affiliate_purchase
import sqlite3
from notificacoes_vencimento import registrar_venda
from remarketing_handler import record_abandonment, remove_abandonment
from price_adjustment import adjust_price
from sale_notification import send_sale_notification  # Import only the necessary function

logger = logging.getLogger(__name__)

REVENDERS_FILE = 'revendedores.json'

def load_revendores():
    if os.path.exists(REVENDERS_FILE):
        with open(REVENDERS_FILE, 'r') as file:
            try:
                data = json.load(file)
                if isinstance(data, dict) and "revendedores" in data:
                    return data
                else:
                    return {"revendedores": {}}
            except json.JSONDecodeError:
                return {"revendedores": {}}
    return {"revendedores": {}}

def save_revendores(data):
    with open(REVENDERS_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def renovar_revendedor_painel(username):
    url = URL_PAINEL_API
    data = {
        'passapi': IOS_API_KEY,
        'module': 'renewrev',
        'user': username
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        logger.info(f"Revendedor {username} renovado com sucesso no painel.")
        return response.text
    else:
        logger.error(f"Erro ao renovar revendedor {username} no painel: {response.text}")
        return None

planos = {
    'usuario_1_30': {
        'nome': 'Plano 1 Pessoa - 30 Dias',
        'preco': 17.00,
        'tipo': 'usuario',
        'usuarios_entregues': 1,
        'validade_dias': 30
    },
    'usuario_2_30': {
        'nome': 'Plano 2 Pessoas - 30 Dias',
        'preco': 27.00,
        'tipo': 'usuario',
        'usuarios_entregues': 2,
        'validade_dias': 30
    },
    'usuario_3_30': {
        'nome': 'Plano 3 Pessoas - 30 Dias',
        'preco': 37.00,
        'tipo': 'usuario',
        'usuarios_entregues': 3,
        'validade_dias': 30
    },
    'usuario_4_30': {
        'nome': 'Plano 4 Pessoas - 30 Dias',
        'preco': 47.00,
        'tipo': 'usuario',
        'usuarios_entregues': 4,
        'validade_dias': 30
    },
    'usuario_1_15': {
        'nome': 'Plano 1 Pessoa - 15 Dias',
        'preco': 10.00,
        'tipo': 'usuario',
        'usuarios_entregues': 1,
        'validade_dias': 15
    },
    'usuario_1_40': {
        'nome': 'Plano 1 Pessoa - 40 Dias',
        'preco': 40.00,
        'tipo': 'usuario',
        'usuarios_entregues': 1,
        'validade_dias': 40
    },
    'revenda_start': {
        'nome': 'Revenda Start - 10 Pessoas',
        'preco': 30.00,  # Atualizado de 40.00 para 30.00
        'tipo': 'revenda',
        'limite': 10,
        'validade_dias': 30
    },
    'revenda_basica': {
        'nome': 'Revenda Básica - 20 Pessoas',
        'preco': 52.50,  # Atualizado de 70.00 para 52.50
        'tipo': 'revenda',
        'limite': 20,
        'validade_dias': 30
    },
    'revenda_intermediaria': {
        'nome': 'Revenda Média - 50 Pessoas',
        'preco': 90.00,  # Atualizado de 120.00 para 90.00
        'tipo': 'revenda',
        'limite': 50,
        'validade_dias': 30
    },
    'revenda_avancada': {
        'nome': 'Revenda Master - 100 Pessoas',
        'preco': 135.00,  # Atualizado de 180.00 para 135.00
        'tipo': 'revenda',
        'limite': 100,
        'validade_dias': 30
    },
    'revenda_premium': {
        'nome': 'Revenda Top - 150 Pessoas',
        'preco': 180.00,  # Atualizado de 240.00 para 180.00
        'tipo': 'revenda',
        'limite': 150,
        'validade_dias': 30
    },
    'revenda_elite': {
        'nome': 'Revenda Elite - 200 Pessoas',
        'preco': 225.00,  # Atualizado de 300.00 para 225.00
        'tipo': 'revenda',
        'limite': 200,
        'validade_dias': 30
    }
}

def salvar_qr_code_base64(qr_code_base64: str, file_path: str) -> None:
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(qr_code_base64))

def register_sale(chat_id, sale_type, amount, buyer_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO sales (sale_date, sale_type, amount, buyer_id, buyer_name)
        VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sale_type, amount, chat_id, buyer_name))
        
        conn.commit()
        logger.info(f"Venda registrada para {buyer_name} (ID: {chat_id}), Tipo: {sale_type}, Valor: {amount}, Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Erro ao registrar a venda para {buyer_name} (ID: {chat_id}): {e}")
    finally:
        conn.close()

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, discount=0, plano_selecionado=None) -> None:
    query = update.callback_query
    await query.answer()

    if plano_selecionado is None:
        plano_selecionado = query.data

    plano_info = planos.get(plano_selecionado)

    if plano_info:
        # Preço original do plano
        preco_original = plano_info['preco']

        # Ajustar o preço caso haja um ajuste ativo
        preco_final = adjust_price(preco_original)

        # Aplicar desconto de remarketing ou outro desconto se houver
        if discount > 0:
            preco_final = preco_final * (1 - discount / 100)
            preco_final = round(preco_final, 2)

        tipo = plano_info['tipo']
        limite = plano_info.get('limite', None)
        usuarios_entregues = plano_info.get('usuarios_entregues', 1)
        validade_dias = plano_info.get('validade_dias', 30)

        # Armazenar informações necessárias no contexto
        context.user_data['payment_info'] = {
            'plano_selecionado': plano_selecionado,
            'preco_final': preco_final,
            'tipo': tipo,
            'limite': limite,
            'usuarios_entregues': usuarios_entregues,
            'validade_dias': validade_dias,
            'discount': discount
        }

        # Mensagem de confirmação personalizada em HTML
        mensagem_preco = (
            f"<b>💰 Preço Original:</b> R$ {preco_original:.2f}\n"
            f"<b>💰 Total a Pagar:</b> R$ {preco_final:.2f}\n"
            if preco_final != preco_original else
            f"<b>💰 Total a Pagar:</b> R$ {preco_final:.2f}\n"
        )

        if tipo == 'usuario': 
            mensagem_confirmacao = (
                "<b>🛒 Complete sua Assinatura e Tenha Acesso Ilimitado!</b>\n\n"
                "📱 <b>Compatível com iOS e Android</b>\n"
                f"📦 <b>Plano Selecionado:</b> {plano_info['nome']}\n"
                "🌐 <b>Internet Ilimitada</b> com cobertura 🟣 VIVO, 🔵 TIM e 🔴 CLARO\n\n"
                "<b>✨ Benefícios Exclusivos:</b>\n"
                "- 🚀 <b>Navegação Privada e Ilimitada</b> – Liberdade total na internet!\n"
                "- 🔒 <b>Conta Exclusiva e Segura</b> – Só para você.\n"
                "- 💻 <b>Aplicativo Oficial</b> – Acesso rápido e fácil para Android.\n"
                "- 📖 <b>Guia de Configuração Rápida</b> – Comece em minutos.\n"
                "- 🤝 <b>Suporte 24h via Telegram</b>: @kriasys_autorizado\n"
                "- 🔁 <b>Link de Renovação Sempre Disponível</b> – Sem complicações.\n\n"
                f"{mensagem_preco}"
                "⚠ <b>Clique em Confirmar para ativar seu acesso e gerar o PIX!</b>"
            )
        elif tipo == 'revenda': 
            mensagem_confirmacao = (
                "<b>📦 Confirme Sua Assinatura e Comece a Revender Internet Ilimitada! 📦</b>\n\n"
                "📱 <b>Compatível com iOS e Android</b>\n"
                f"<b>🔹 Plano Selecionado:</b> {plano_info['nome']}\n"
                "🌐 <b>Serviço:</b> Internet Ilimitada para seus clientes com cobertura 🟣 VIVO, 🔵 TIM e 🔴 CLARO\n\n"
                "<b>✨ Benefícios Exclusivos para Revendedores:</b>\n"
                "- 🛠️ <b>Painel Completo</b> – Crie e gerencie contas de clientes com facilidade.\n"
                "- 💼 <b>Configuração de Sub-revendas</b> – Expanda seus negócios sem limites!\n"
                "- 🧪 <b>Testes Ilimitados</b> – Atraia novos clientes com acesso de teste.\n"
                "- 📲 <b>Aplicativo Oficial</b> – Facilidade de uso para seus clientes Android.\n"
                "- 📖 <b>Tutoriais de Configuração</b> – Simples e rápido para começar.\n"
                "- 💬 <b>Suporte Exclusivo via Telegram</b>: Atendimento direto em @kriasys_autorizado e @pedrooo\n\n"
                f"{mensagem_preco}"
                "⚠️ <b>Clique em Confirmar Compra para desbloquear seu painel de controle e iniciar sua revenda!</b>"
            )

        # Botão de confirmação
        keyboard = [[InlineKeyboardButton("Confirmar Pagamento", callback_data=f"confirmar_{plano_selecionado}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Verifica se a mensagem anterior é uma foto ou uma mensagem de texto
        try:
            await query.edit_message_text(text=mensagem_confirmacao, reply_markup=reply_markup, parse_mode='HTML')
        except:
            await query.delete_message()
            await context.bot.send_message(chat_id=query.message.chat_id, text=mensagem_confirmacao, reply_markup=reply_markup, parse_mode='HTML')
        
        logger.info(f"Mensagem de confirmação enviada para o usuário {query.message.chat_id}")

async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Extrai o plano a partir do callback_data
    plano_selecionado = query.data.replace("confirmar_", "")
    payment_info = context.user_data.get('payment_info', {})

    # Verifica se o plano selecionado corresponde ao armazenado
    if payment_info.get('plano_selecionado') != plano_selecionado:
        await query.edit_message_text(text="Erro: informações de pagamento inconsistentes.")
        return

    preco_final = payment_info['preco_final']
    tipo = payment_info['tipo']
    limite = payment_info.get('limite', None)
    usuarios_entregues = payment_info.get('usuarios_entregues', 1)
    validade_dias = payment_info.get('validade_dias', 30)

    payer_info = {
        "email": PAYER_EMAIL,
        "first_name": PAYER_FIRST_NAME,
        "last_name": PAYER_LAST_NAME,
        "identification": {
            "type": PAYER_IDENTIFICATION_TYPE,
            "number": PAYER_IDENTIFICATION_NUMBER
        }
    }

    qr_code_data = gerar_qr_code_mercado_pago(preco_final, payer_info)

    if not qr_code_data:
        message = "Erro ao obter o QR Code."
        await query.edit_message_text(text=message)
    else:
        qr_code = qr_code_data['qr_code']
        qr_code_base64 = qr_code_data['qr_code_base64']
        image_path = f"qrcodes/{plano_selecionado}_{query.message.chat.id}.png"
        salvar_qr_code_base64(qr_code_base64, image_path)

        # Apagar a mensagem de confirmação antes de enviar o QR code
        await query.delete_message()

        with open(image_path, 'rb') as qr_image:
            await query.message.reply_photo(photo=InputFile(qr_image), caption="Escaneie o QR code para pagar.")

        message = (
            f"<b>🚀 Conclua seu Pagamento!</b>\n\n"
            f"<b>Plano Selecionado:</b> {planos[plano_selecionado]['nome']}\n"
            f"<b>Valor a Pagar:</b> R$ {preco_final:.2f}\n\n"
            "📲 <b>Passo 1:</b> Escaneie o QR Code para pagar rapidamente.\n\n"
            "📌 <b>Passo 2:</b> Caso prefira, utilize o código Pix abaixo:\n\n"
            f"<code>{qr_code}</code>\n\n"
            "⚠️ <b>Atenção:</b> Após o pagamento, seu acesso será ativado automaticamente!"
        )
        await query.message.reply_text(text=message, parse_mode='HTML')
        logger.info(f"QR Code enviado para o usuário {query.message.chat_id}")

        # Inicia a verificação do pagamento
        asyncio.create_task(verificar_pagamento_pix(
            mp, qr_code_data['id'], query.message.chat.id, context, tipo, preco_final, limite, usuarios_entregues, validade_dias
        ))

async def process_successful_payment(chat_id: int, context: ContextTypes.DEFAULT_TYPE, tipo: str, preco_final: float, limite: int, usuarios_entregues: int, validity_days: int):
    data_compra = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    chat_info = await context.bot.get_chat(chat_id)
    nome_comprador = chat_info.first_name
    id_comprador = chat_id
    purchase_id = f"{chat_id}-{int(datetime.now().timestamp())}"  # Gera um ID único para a compra

    register_sale(chat_id, tipo, preco_final, nome_comprador)

    # Obtém o plano selecionado
    plano_selecionado = context.user_data['payment_info']['plano_selecionado']
    service_name = planos[plano_selecionado]['nome']

    # Envia a notificação de venda para o canal de controle financeiro
    await send_sale_notification(
        customer_name=nome_comprador,
        service_name=service_name,
        customer_id=str(id_comprador),
        purchase_id=purchase_id,
        destination_chat_id=TELEGRAM_CONTROL_CHANNEL_ID  # Send to control channel
    )

    # Registra a venda no arquivo JSON para notificações de vencimento
    registrar_venda(chat_id, tipo, validity_days)

    # Remove o registro de abandono, se houver
    remove_abandonment(chat_id)

    revendedores = load_revendores()

    if tipo == "usuario":
        user_limit = usuarios_entregues
        username, user_message = create_user_for_sale(user_limit=user_limit, validity_days=validity_days)
        if user_message:
            await context.bot.send_message(chat_id=chat_id, text=user_message, parse_mode="HTML", disable_web_page_preview=True)
            logger.info(f"Mensagem de usuário enviada para {chat_id}")

            # Notificação no grupo público de vendas
            canal_message = (
                f"🎉 Usuário Vendido 🎉\n"
                f"📅 Data da Compra: {data_compra}\n"
                f"👤 Comprador: {nome_comprador} (ID: {id_comprador})\n"
                f"🗝 Usuário gerado: {username}"
            )
            await context.bot.send_message(chat_id=TELEGRAM_SALES_GROUP_ID, text=canal_message, parse_mode="HTML", disable_web_page_preview=True)
            logger.info(f"Mensagem de venda enviada para o grupo de vendas (ID: {TELEGRAM_SALES_GROUP_ID})")

    elif tipo == "revenda" and limite:
        if str(chat_id) in revendedores["revendedores"]:
            reseller_info = revendedores["revendedores"][str(chat_id)]
            username = reseller_info["username"]

            resultado_renovacao = renovar_revendedor_painel(username)
            if resultado_renovacao:
                validade_antiga = datetime.strptime(reseller_info["validade"], "%d/%m/%Y")
                nova_validade = (validade_antiga + timedelta(days=validity_days)).strftime("%d/%m/%Y")
                reseller_info["validade"] = nova_validade
                reseller_info["data_compra"] = data_compra

                save_revendores(revendedores)

                reseller_message = (
                    f"🔄 <b>Renovação de Revendedor</b> 🔄\n\n"
                    f"🔍 <b>Revendedor:</b> <code>{username}</code>\n"
                    f"📅 <b>Nova Validade:</b> {nova_validade}\n"
                )
            else:
                reseller_message = "Erro ao renovar revendedor no painel. Por favor, tente novamente mais tarde."
        else:
            username, reseller_message = create_reseller(limit=limite, notify=False)
            if username:
                validade = (datetime.now() + timedelta(days=validity_days)).strftime("%d/%m/%Y")
                revendedores["revendedores"][str(chat_id)] = {
                    "username": username,
                    "limite": limite,
                    "data_compra": data_compra,
                    "validade": validade
                }
                save_revendores(revendedores)
            else:
                reseller_message = "Erro ao criar revendedor. Por favor, tente novamente mais tarde."

        await context.bot.send_message(chat_id=chat_id, text=reseller_message, parse_mode="HTML", disable_web_page_preview=True)
        logger.info(f"Mensagem de revendedor enviada para {chat_id}")

        # Notificação no grupo público de vendas
        canal_message = (
            f"💰 <b>Revenda Vendida</b> 💰\n"
            f"📅 Data da Compra: {data_compra}\n"
            f"👤 Comprador: {nome_comprador} (ID: {id_comprador})\n"
            f"🗝 Revenda gerada: {username}"
        )
        await context.bot.send_message(chat_id=TELEGRAM_SALES_GROUP_ID, text=canal_message, parse_mode="HTML", disable_web_page_preview=True)
        logger.info(f"Mensagem de revenda enviada para o grupo de vendas (ID: {TELEGRAM_SALES_GROUP_ID})")

    referrer_id = context.user_data.get('referrer_id')
    if referrer_id:
        logger.info(f"Registrando compra do usuário {chat_id} referenciado pelo afiliado {referrer_id}")
        await record_affiliate_purchase(referrer_id, chat_id, context)

async def verificar_pagamento_pix(mp, id_pagamento, chat_id, context, tipo, preco_final, limite: int, usuarios_entregues: int, validity_days: int):
    start_time = time.time()  # Marca o início do tempo de verificação
    timeout = 20 * 60  # 20 minutos em segundos
    
    while True:
        elapsed_time = time.time() - start_time
        
        if elapsed_time > timeout:
            logger.info(f"Tempo limite atingido para o pagamento {id_pagamento}. Interrompendo verificação.")
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ <b>Tempo de pagamento expirado.</b>\n\nO pagamento não foi concluído dentro do período de 20 minutos. Se ainda desejar contratar o serviço, por favor, faça uma nova solicitação e realize o pagamento novamente.",
                parse_mode="HTML"
            )
            # Registra o abandono de PIX
            record_abandonment(chat_id, id_pagamento)
            break

        logger.info(f"Verificando pagamento {id_pagamento}...")
        pagamento_info = mp.get_pagamento(id_pagamento)
        status = pagamento_info.get('status')
        logger.info(f"Status do pagamento {id_pagamento}: {status}")
        
        if status == 'approved':
            await process_successful_payment(chat_id, context, tipo, preco_final, limite, usuarios_entregues, validity_days)
            # Remove qualquer registro de abandono para este usuário
            remove_abandonment(chat_id)
            break
        
        await asyncio.sleep(60)  # Espera 1 minuto antes de verificar novamente

# Adicione os handlers necessários no seu arquivo principal
def setup_payment_handlers(application):
    # Handler para confirmar o pagamento com padrão mais específico para evitar conflitos
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern='^confirmar_(?!teste$).*'))
