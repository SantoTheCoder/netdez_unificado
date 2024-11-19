#notificacoes_vencimento.py
import json
import os
import asyncio
from datetime import datetime, timedelta
from telegram import Bot
from config import API_KEY

VENDAS_FILE = 'vendas.json'
bot = Bot(token=API_KEY)

def registrar_venda(cliente_id, tipo_compra, validade_dias):
    """
    Registra uma nova venda no arquivo vendas.json.
    """
    data_compra = datetime.now()
    data_vencimento = data_compra + timedelta(days=validade_dias)
    
    nova_venda = {
        "cliente_id": cliente_id,
        "tipo_compra": tipo_compra,
        "data_compra": data_compra.strftime("%Y-%m-%d %H:%M:%S"),
        "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
        "notificacoes_enviadas": {
            "dois_dias_antes": False,
            "um_dia_antes": False,
            "no_dia": False
        }
    }
    
    if os.path.exists(VENDAS_FILE):
        with open(VENDAS_FILE, 'r+') as file:
            vendas = json.load(file)
            vendas.append(nova_venda)
            file.seek(0)
            json.dump(vendas, file, indent=4)
    else:
        with open(VENDAS_FILE, 'w') as file:
            json.dump([nova_venda], file, indent=4)

    print(f"Venda registrada: {nova_venda}")

async def enviar_notificacao(cliente_id, mensagem):
    """
    Envia uma mensagem de notificação para o cliente no Telegram.
    """
    try:
        await bot.send_message(chat_id=cliente_id, text=mensagem, parse_mode="Markdown")
        print(f"Notificação enviada para {cliente_id}: {mensagem}")
    except Exception as e:
        print(f"Erro ao enviar notificação para {cliente_id}: {e}")

async def verificar_vencimentos():
    """
    Verifica o arquivo vendas.json para encontrar vencimentos próximos e enviar notificações.
    """
    if not os.path.exists(VENDAS_FILE):
        print("Nenhuma venda registrada.")
        return
    
    with open(VENDAS_FILE, 'r+') as file:
        vendas = json.load(file)
        hoje = datetime.now().date()
        vendas_atualizadas = []

        for venda in vendas:
            data_vencimento = datetime.strptime(venda["data_vencimento"], "%Y-%m-%d").date()
            dias_para_vencimento = (data_vencimento - hoje).days
            cliente_id = venda["cliente_id"]
            tipo_compra = venda["tipo_compra"]
            notificacoes = venda["notificacoes_enviadas"]
            
            if dias_para_vencimento == 2 and not notificacoes["dois_dias_antes"]:
                if tipo_compra == "usuario":
                    mensagem = (
                        "🕑 *Atenção!* Sua Internet Ilimitada vence em 2 dias. "
                        "Renove agora para continuar navegando sem interrupções!"
                    )
                else:
                    mensagem = (
                        "🕑 *Atenção!* Sua Internet Ilimitada Revenda vence em 2 dias. "
                        "Renove já para evitar que seus clientes fiquem sem internet!"
                    )
                await enviar_notificacao(cliente_id, mensagem)
                notificacoes["dois_dias_antes"] = True

            elif dias_para_vencimento == 1 and not notificacoes["um_dia_antes"]:
                if tipo_compra == "usuario":
                    mensagem = (
                        "⏰ *Última Chamada!* Sua Internet Ilimitada vence amanhã. "
                        "Garanta sua conexão renovando hoje!"
                    )
                else:
                    mensagem = (
                        "⏰ *Última Chamada!* Sua Internet Ilimitada Revenda vence amanhã. "
                        "Renove agora e mantenha seus clientes conectados!"
                    )
                await enviar_notificacao(cliente_id, mensagem)
                notificacoes["um_dia_antes"] = True

            elif dias_para_vencimento == 0 and not notificacoes["no_dia"]:
                if tipo_compra == "usuario":
                    mensagem = (
                        "🚨 *Hoje é o Dia!* Sua Internet Ilimitada vence hoje. "
                        "Renove imediatamente e mantenha-se online!"
                    )
                else:
                    mensagem = (
                        "🚨 *Hoje é o Dia!* Sua Internet Ilimitada Revenda vence hoje. "
                        "Renove imediatamente para garantir que seus clientes não fiquem sem conexão!"
                    )
                await enviar_notificacao(cliente_id, mensagem)
                notificacoes["no_dia"] = True

            vendas_atualizadas.append(venda)

        # Salvar as atualizações no arquivo JSON
        file.seek(0)
        json.dump(vendas_atualizadas, file, indent=4)
        file.truncate()

async def verificar_vencimentos_periodicamente(intervalo_segundos=86400):
    """
    Verifica os vencimentos periodicamente a cada intervalo definido.
    O padrão é executar a verificação uma vez por dia (86400 segundos).
    """
    while True:
        print("Iniciando verificação de vencimentos...")
        await verificar_vencimentos()
        print(f"Verificação concluída. Próxima verificação em {intervalo_segundos} segundos.")
        await asyncio.sleep(intervalo_segundos)
