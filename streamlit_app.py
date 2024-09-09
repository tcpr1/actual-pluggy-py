import streamlit as st
from functions import pluggy_sync, backup_actual
from datetime import datetime, timedelta

# Lista de instâncias Actual: Nome:Porta
actual_users = {"": "", "Thiago": "5006", "Milena": "5008", "Família": "5007", "Fabio": "5011","Teste": "5077"}
url_base = "http://elite.mt:"

st.header("Actual-Pluggy-Py")
st.write("Brazilian bank sync for Actual powered by Pluggy")
st.divider()

# Criando as colunas
col1, col2 = st.columns([2, 1])

# Coluna da esquerda
with col1:
    # Campo para selecionar o usuário (instância do Actual)
    selected_user = st.selectbox("Selecione o usuário:", list(actual_users.keys()))
    # Obter o valor selecionado a partir do dicionário e concatenar com a url base
    URL_ACTUAL = url_base + actual_users[selected_user]
    # Campo para o usuário preencher a senha
    PASSWORD_ACTUAL = st.text_input("Senha do Actual:", type="password")
    # Campo para o usuário informar o nome de um arquivo
    FILE_ACTUAL = st.text_input("Nome do budget (file):")

# Coluna da direita
with col2:
    # Definindo datas default
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=7)

    # Campos de data
    start_date = st.date_input("Data de Início", start_date, format="DD/MM/YYYY")
    end_date = st.date_input("Data de Fim", end_date, format="DD/MM/YYYY")

# Exibição dos valores
st.write("URL Actual:", URL_ACTUAL)
# st.write("Senha Actual:", PASSWORD_ACTUAL)
st.write("Arquivo Budget Actual:", FILE_ACTUAL)

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
        output0.write("Realizando backup...")
        backup_actual(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL)
        output0.write("Backup concluído.")
        
        with open(f"./Backup/{FILE_ACTUAL}-{end_date.strftime('%Y%m%d')}.zip", "rb") as file:
            btn = st.download_button(
                label="Download backup",
                data=file,
                file_name=(f"{selected_user}-{FILE_ACTUAL}-{end_date.strftime('%Y%m%d')}.zip"),
                mime="file",
                help=(f"{selected_user}-{FILE_ACTUAL}-{end_date.strftime('%Y%m%d')}.zip"),
            )
        
        output1.write("Iniciando sincronização...")
        
        output2 = st.empty()
        with st_capture(output2.code):    
            delta = end_date - start_date
            # Limitando as consultas ao pluggy para 10 dias por vez
            if delta.days <= 10:
                start_date = start_date.strftime('%Y-%m-%d')
                end_date = end_date.strftime('%Y-%m-%d')
                pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, start_date, end_date)
            else:
                for i in range(0, delta.days + 1, 10):
                    step_start_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                    step_end_date = min(start_date + timedelta(days=i + 9), end_date).strftime('%Y-%m-%d')
                    print(f"\nExecutando sync entre datas: {step_start_date} e {step_end_date}")
                    pluggy_sync(URL_ACTUAL, PASSWORD_ACTUAL, FILE_ACTUAL, step_start_date, step_end_date)
            output1.write("Sincronização concluída.")
