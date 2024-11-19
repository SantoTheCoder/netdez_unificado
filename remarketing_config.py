# remarketing_config.py
# Configurações para o sistema de remarketing

# Configurações de remarketing existentes
DISCOUNT_PERCENTAGE = 20  # Percentual de desconto da oferta especial
REMARKETING_DELAY_HOURS = 24  # Horas após o abandono para enviar a oferta
OFFER_VALIDITY_HOURS = 24  # Validade da oferta especial
PROMOTIONAL_IMAGE = 'imagem1.jpg'  # Nome da imagem promocional
PROMOTIONAL_TEXT = f"""
🎁 *Oferta Especial para Você!*

Notamos que você iniciou uma compra mas não a concluiu. Queremos oferecer uma oferta exclusiva de *{DISCOUNT_PERCENTAGE}% de desconto* para você finalizar sua compra!

Clique no botão abaixo para aproveitar esta oferta especial. Mas corra, é por tempo limitado!
"""

# Intervalo de verificação de remarketing
REMARKETING_CHECK_INTERVAL_SECONDS = 3600  # Defina para 3600 (1 hora) para produção

# remarketing_config.py
# Configurações para o FAQ com links diretos do canal público

FAQ_VIDEO_FILES = {
    'tutorial1': 'https://t.me/g81ds81d15faq/3',
    'tutorial2': 'https://t.me/g81ds81d15faq/4',
    'tutorial3': 'https://t.me/g81ds81d15faq/5',
    'tutorial4': 'https://t.me/g81ds81d15faq/7'
}

FAQ_TEXTS = {
    'tutorial1': "Vídeo 1: Mostrando como usar a internet ilimitada para navegar sem limites.",
    'tutorial2': "Vídeo 2: Como funciona o sistema de revendedores. Assista ao vídeo!",
    'tutorial3': "Vídeo 3: Veja como realizar compras para usuários e revendedores.",
    'tutorial4': "Vídeo 4: Como fazer autoatendimento e resolver problemas de conexão."
}
