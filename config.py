# configG.py
import os

# Configurações e variáveis de ambiente
API_KEY = os.getenv('TELEGRAM_API_KEY', '5889524682:AAHbpTe56tQbE5A5UHFXBDCdygHhWpttEf4')
IOS_API_KEY = os.getenv('IOS_API_KEY', '38mLyr38aEdGHFaGjfJJEiZHWs')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1002225678009')
DEFAULT_VALIDITY_DAYS = 30
DEFAULT_USER_LIMIT = 1
DEFAULT_RESELLER_LIMIT = 10

# Configurações do MercadoPago
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', 'APP_USR-1062519597180352-070416-90b9d92c9d0edc48f826dc34266ceb2e-585772932')
CHAVE_PIX = os.getenv('CHAVE_PIX', '28d812de-5fe9-4864-a3b2-d684e1ac4fe5')

# Nome e contato do bot
BOT_NAME = os.getenv('BOT_NAME', '@netdez_bot')
SUPPORT_CONTACT = os.getenv('SUPPORT_CONTACT', '@Pedrooo')
ADMIN_ID = os.getenv('ADMIN_ID', '5197753914')

# Configurações API Painel 
URL_PAINEL_API = os.getenv('URL_PAINEL_API', 'https://painel.netdez.site/core/apiatlas.php')
URL_RESELLERS = os.getenv('URL_RESELLERS', 'https://painel.netdez.site/')
RENEWAL_LINK = os.getenv('RENEWAL_LINK', 'https://painel.netdez.site/renovar.php')

# Configurações do Mercado Pago - Pagamento 
PAYER_EMAIL = os.getenv('PAYER_EMAIL', 'netdez@gmail.com')
PAYER_FIRST_NAME = os.getenv('PAYER_FIRST_NAME', 'android')
PAYER_LAST_NAME = os.getenv('PAYER_LAST_NAME', 'netdez')
PAYER_IDENTIFICATION_TYPE = os.getenv('PAYER_IDENTIFICATION_TYPE', 'CPF')
PAYER_IDENTIFICATION_NUMBER = os.getenv('PAYER_IDENTIFICATION_NUMBER', '08005204833')

# Configurações de Links de Aplicativos
IOS_APP_LINK = os.getenv('IOS_APP_LINK', 'https://apps.apple.com/us/app/npv-tunnel/id1629465476')
CONFIG_FILES_LINK = os.getenv('CONFIG_FILES_LINK', 'https://t.me/+R72mmGw8JMdiZWEx')
ANDROID_APP_LINK = os.getenv('ANDROID_APP_LINK', 'https://www.mediafire.com/file/hilzrl87bnr1arn/NET10+_+3.3+_+INTERNET+ILIMITADA.apk/file')

# Configurações de Canal e Aplicativo
CHANNEL_ID = os.getenv('CHANNEL_ID', '-1002379939880')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@CA90298APLICA123')
APP_MESSAGE_ID = os.getenv('APP_MESSAGE_ID', '3')
BOT_LINK_DESTINO = os.getenv('BOT_LINK_DESTINO', 'https://t.me/NetDez_Bot')

# Configurações de Grupos de Controle
TELEGRAM_SALES_GROUP_ID = -1002364091260
TELEGRAM_CONTROL_CHANNEL_ID = -1002364091260
TELEGRAM_CHAT_USERNAME = "@TF81S8D165"

# Configurações de Simulação de Vendas
SIMULATE_SALES_AUTOMATICALLY = True
MIN_DAILY_SALES = 5  # Ajustado para refletir uma faixa de vendas um pouco mais alta
MAX_DAILY_SALES = 12  # Para adicionar realismo em dias com mais movimento
BASE_SALES_INTERVAL = 45  # Intervalo médio ajustado entre vendas para maior variabilidade

# Configurações de Horários de Pico para Simulação de Vendas
PEAK_HOURS = {
    "morning": {"start": 8, "end": 12, "probability": 0.25},   # Ajuste no pico matutino
    "afternoon": {"start": 12, "end": 18, "probability": 0.4},  # Intensificado na tarde
    "evening": {"start": 18, "end": 23, "probability": 0.45},   # Maior probabilidade no horário noturno
    "night": {"start": 23, "end": 8, "probability": 0.15}       # Período de madrugada com menor chance
}

# Distribuição de Vendas Diárias por Período
SALES_DISTRIBUTION = {
    "madrugada": 5,   # 00h-06h
    "manhã": 25,      # 06h-12h
    "tarde": 35,      # 12h-18h
    "noite": 35       # 18h-00h
}

# Probabilidades de Tipo de Venda
USER_SALE_PROBABILITY = 85  # Ajustado para equilibrar mais usuários e revendedores
RESELLER_SALE_PROBABILITY = 15

# Probabilidades de Planos Específicos
USER_PLAN_PROBABILITIES = {
    "Plano 1 Pessoa - 30 Dias": 55,   # Ajuste para refletir mudanças sazonais
    "Plano 1 Pessoa - 40 Dias": 22,
    "Plano 1 Pessoa - 15 Dias": 8,
    "Plano 2 Pessoas - 30 Dias": 10,
    "Plano 3 Pessoas - 30 Dias": 3,
    "Plano 4 Pessoas - 30 Dias": 2
}

RESELLER_PLAN_PROBABILITIES = {
    "Revenda Start - 10 Pessoas": 55,   # Ajuste para uma distribuição mais realista
    "Revenda Básica - 20 Pessoas": 22,
    "Revenda Intermediária - 50 Pessoas": 15,
    "Revenda Avançada - 100 Pessoas": 5,
    "Revenda Premium - 150 Pessoas": 2,
    "Revenda Elite - 200 Pessoas": 1
}

# config.py
SIMULATE_SALES_AUTOMATICALLY = True  # Define como False para desativar o sistema
