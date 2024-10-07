import streamlit as st
from functions import pluggy_sync, backup_actual, get_pluggy_api
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
USERS = ["Criar Novo"] + read_users()

if CONFIG['streamlit'] == 'True':
    st.header("Actual-Pluggy-Py")
    st.write("Brazilian bank sync for Actual powered by Pluggy - v06_10_2024.2")
    st.divider()

    # Criando as colunas
    col1, col2 = st.columns([2, 1])

    # Coluna da esquerda
    with col1:
        # Campo para selecionar o usuário (instância do Actual)
        # selected_user = st.selectbox("Selecione o usuário:", list(actual_users.keys()))
        selected_user = st.selectbox("Selecione o usuário:", list(USERS))
        # Obter o valor selecionado a partir do dicionário e concatenar com a url base
        # URL_ACTUAL = url_base + actual_users[selected_user]
        if selected_user != "Criar Novo":
            user_data = read_user_config(selected_user)
            URL_ACTUAL = user_data['url']
            PASSWORD_ACTUAL = user_data['pass']
            FILE_ACTUAL = user_data['file']
            EXT_URL = user_data['ext_url']
            st.write(EXT_URL)

        # Entrada manual das informações e salvar em config.ini
        else:
            NEW_USER = st.text_input("Usuário:")
            # Campo para o usuário preencher a senha
            PASSWORD_ACTUAL = st.text_input("Senha do Actual:", type="password")
            # Campo para o usuário informar o nome de um arquivo
            FILE_ACTUAL = st.text_input("Nome do budget (file):")
            URL_ACTUAL = st.text_input("URL do Actual (local):")
            EXT_URL = st.text_input("URL externa do Actual:")
            # Botão para executar a função pluggy_sync
            if st.button("Cadastrar Usuário"):
                # add a new section and some values
                config = configparser.ConfigParser()
                config.read('data/config.ini', encoding='utf-8')
                config.add_section(NEW_USER)
                config.set(NEW_USER, 'url', URL_ACTUAL)
                config.set(NEW_USER, 'pass', PASSWORD_ACTUAL)
                config.set(NEW_USER, 'file', FILE_ACTUAL)
                config.set(NEW_USER, 'ext_url', EXT_URL)
                # save to a file
                with open('data/config.ini', 'w', encoding='utf-8') as configfile:
                    config.write(configfile)

    # Coluna da direita
    with col2:
        # Definindo datas default
        end_date_default = datetime.today().replace(tzinfo=ZoneInfo('America/Sao_Paulo')).date()
        current_date = end_date_default.strftime("%Y%m%d")
        start_date_default = end_date_default - timedelta(days=3)

        # Campos de data
        start_date = st.date_input("Data de Início", start_date_default, format="DD/MM/YYYY")
        end_date = st.date_input("Data de Fim", end_date_default, format="DD/MM/YYYY")

    # Bloco para capturar e poder exibir os print() do código (output2)
    from contextlib import contextmanager, redirect_stdout
    from io import StringIO
    from time import sleep
    @contextmanager
    def st_capture(output_func):
        with StringIO() as stdout, redirect_stdout(stdout):
            old_write = stdout.write

            def new_write(string):
                ret = old_write(string)
                output_func(stdout.getvalue())
                return ret
            stdout.write = new_write
            yield

    st.divider()

    col1, col2 = st.columns([2, 1])
    with col2:
        output0 = st.empty()
        output1 = st.empty()
        
    with col1:
        # Botão para executar a função pluggy_sync
        if st.button("**SYNC**"):
            try:
                # Primeiro busca pluggy API key - em caso de falha, levanta erro
                apiKey = get_pluggy_api(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)

                # output0.write("Realizando backup...")
                # backup_actual(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)
                # output0.write("Backup concluído.")
                # with open(f"./data/Backup/{FILE_ACTUAL}-{current_date}.zip", "rb") as file:
                #     btn = st.download_button(
                #         label="Download backup",
                #         data=file,
                #         file_name=(f"{selected_user}-{FILE_ACTUAL}-{current_date}.zip"),
                #         mime="file",
                #         help=(f"{selected_user}-{FILE_ACTUAL}-{current_date}.zip"),
                #     )
                
                output1.write("Iniciando sincronização...")
                output2 = st.empty()
                with st_capture(output2.code):    
                    delta = end_date - start_date
                    # Limitando as consultas ao pluggy para 10 dias por vez
                    if delta.days <= 10:
                        start_date = start_date.strftime('%Y-%m-%d')
                        end_date = end_date.strftime('%Y-%m-%d')
                        pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, start_date, end_date, apiKey)
                    else:
                        for i in range(0, delta.days + 1, 10):
                            step_start_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                            step_end_date = min(start_date + timedelta(days=i + 9), end_date).strftime('%Y-%m-%d')
                            print(f"\nExecutando sync entre datas: {step_start_date} e {step_end_date}")
                            pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, step_start_date, step_end_date, apiKey)
                    output1.write("Sincronização concluída.")
            except ValueError:
                output0.write("Falha: verifique credenciais Pluggy.")
else:
    st.header("Actual-Pluggy-Py")
    st.write("Brazilian bank sync for Actual powered by Pluggy - v06_10_2024.1")
    st.write("Streamlit funcionality disabled - change in config.ini")