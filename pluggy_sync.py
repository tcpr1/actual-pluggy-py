from functions import pluggy_sync, get_pluggy_api
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import configparser

# Funções para ler config.ini
def read_default_config():
    config = configparser.ConfigParser()
    config.read('data/config.ini', encoding='utf-8')
    config_defaults = {
        'streamlit': config['DEFAULT']['streamlit'],
        'sync_interval': config['DEFAULT']['sync_interval']
        }
    return config_defaults

def read_users():
    config = configparser.ConfigParser()
    config.read('data/config.ini', encoding='utf-8')
    users = config.sections()
    return users

def read_user_config(user):
    config = configparser.ConfigParser()
    config.read('data/config.ini', encoding='utf-8')
    config_values = {
        # 'user': user,
        'url': config.get(user,'url'),
        'pass': config.get(user,'pass'),
        'file': config.get(user,'file'),
        'ext_url': config.get(user,'ext_url')
        }
    return config_values

# Ler seção DEFAULT em config.ini
CONFIG = read_default_config()
# Buscar usuários em config.ini (seção = usuário)
USERS = read_users()

for USER in USERS:
    user_data = read_user_config(USER)
    URL_ACTUAL = user_data['url']
    PASSWORD_ACTUAL = user_data['pass']
    FILE_ACTUAL = user_data['file']

    try:
        # Busca pluggy API key - em caso de falha, levanta erro
        apiKey = get_pluggy_api(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)

        # Definindo datas default
        end_date_default = datetime.today().replace(tzinfo=ZoneInfo('America/Sao_Paulo')).date()
        start_date_default = end_date_default - timedelta(days=2)
        # Data formatada
        start_date = start_date_default.strftime('%Y-%m-%d')
        end_date = end_date_default.strftime('%Y-%m-%d')

        print(f"Iniciando sincronização: {USER}")
        tsync_start = datetime.today()
        pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, start_date, end_date, apiKey)
        print(f"Sincronização concluída. | Duração: {datetime.today()-tsync_start}")

    except ValueError:
        print("Falha: verifique credenciais Pluggy.")
        
        