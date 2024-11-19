#SALES.PY
import logging
from datetime import datetime, timedelta
from utils import make_request, generate_random_string
from config import IOS_API_KEY, IOS_APP_LINK, CONFIG_FILES_LINK, ANDROID_APP_LINK, RENEWAL_LINK

logger = logging.getLogger(__name__)

# Tabela de preços com variações de logins e durações
USER_PLANS = {
    ('1', '15'): {'preco': 10.00, 'dias': 15},
    ('1', '30'): {'preco': 17.00, 'dias': 30},
    ('1', '40'): {'preco': 20.00, 'dias': 40},
    ('2', '30'): {'preco': 27.00, 'dias': 30},
    ('3', '30'): {'preco': 37.00, 'dias': 30},
    ('4', '30'): {'preco': 47.00, 'dias': 30}
}

def create_user_for_sale(user_limit, validity_days, admincid=1):
    username = generate_random_string(11)
    password = generate_random_string(11)
    validity_date = (datetime.now() + timedelta(days=validity_days)).strftime("%d/%m/%Y")
    
    api_data = {
        'passapi': IOS_API_KEY,
        'module': 'criaruser',
        'user': username,
        'pass': password,
        'validadeusuario': validity_days,
        'userlimite': user_limit,
        'whatsapp': "1234567890",
        'admincid': admincid
    }

    result = make_request(api_data)

    if 'error' not in result:
        user_message = (
            "<b>🎉 Usuário Criado com Sucesso! 🎉</b>\n\n"
            f"<b>🔎 Usuário:</b>\n<code>{username}</code>\n\n"
            f"<b>🔑 Senha:</b>\n<code>{password}</code>\n\n"
            f"<b>🎯 Validade:</b>\n<code>{validity_date}</code>\n\n"
            f"<b>🕟 Limite de Conexões:</b>\n<code>{user_limit}</code>\n\n"
            "<b>📱 Aplicativos e Arquivos de Configuração:</b>\n\n"
            f"- <b>Para Android:</b>\n"
            f"  - <a href=\"{ANDROID_APP_LINK}\">Baixe o Aplicativo Aqui</a>\n\n"
            f"🌍 <a href=\"{RENEWAL_LINK}\">Link de Renovação (Clique Aqui)</a>\n"
            "Use este link para realizar suas renovações futuras."
        )
        logger.info(f"Usuário {username} criado com sucesso.")
        return username, user_message
    else:
        logger.error(f"Erro ao criar o usuário {username}: {result}")
        return None, "Erro ao criar o usuário. Por favor, verifique manualmente."

def get_user_plan_price(user_limit, validity_days):
    """Retorna o preço de acordo com o limite de usuários e validade"""
    plan_key = (str(user_limit), str(validity_days))
    plan = USER_PLANS.get(plan_key)
    if plan:
        return plan['preco']
    else:
        logger.error(f"Plano não encontrado para {user_limit} logins e {validity_days} dias")
        return None
