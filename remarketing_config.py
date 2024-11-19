# remarketing_config.py
# Configurações para o sistema de remarketing e FAQs

# -----------------------------------
# Configurações de Remarketing
# -----------------------------------

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

# -----------------------------------
# Configurações de FAQ com links diretos do canal público
# -----------------------------------

FAQ_VIDEO_FILES = {
    'tutorial1_android': 'https://t.me/g81ds81d15faq/3',
    'tutorial2_android': 'https://t.me/g81ds81d15faq/4',
    'tutorial3_android': 'https://t.me/g81ds81d15faq/5',
    'tutorial4_android': 'https://t.me/g81ds81d15faq/7',
    'tutorial1_ios': 'https://t.me/g81ds81d15faq/8',
    'tutorial2_ios': 'https://t.me/g81ds81d15faq/9',
    'tutorial3_ios': 'https://t.me/g81ds81d15faq/10',
    'tutorial4_ios': 'https://t.me/g81ds81d15faq/7',  # Verifique se este link está correto para iOS
}

FAQ_TEXTS_ANDROID = {
    'tutorial1_android': "<b>Internet Ilimitada Android</b>\nAssista ao vídeo para aprender a navegar sem limites.",
    'tutorial2_android': "<b>Sistema de Revendedores Android</b>\nEntenda como funciona o sistema de revenda. Veja o vídeo!",
    'tutorial3_android': "<b>Compras para Usuários e Revendedores</b>\nAprenda a realizar compras de forma prática.",
    'tutorial4_android': "<b>Autoatendimento e Conexão</b>\nResolva problemas de conexão para você e seus clientes com nosso vídeo sobre autoatendimento."
}

FAQ_TEXTS_IOS = {
    'tutorial1_ios': "<b>Internet Ilimitada iOS</b>\nAssista ao vídeo para aprender a navegar sem limites.",
    'tutorial2_ios': "<b>Sistema de Revendedores Android + iOS</b>\nEntenda como funciona o sistema de revenda. Veja o vídeo!",
    'tutorial3_ios': "<b>Compras para Usuários e Revendedores</b>\nAprenda a realizar compras de forma prática.",
    'tutorial4_ios': "<b>Autoatendimento e Conexão</b>\nResolva problemas de conexão para você e seus clientes com nosso vídeo sobre autoatendimento."
}
