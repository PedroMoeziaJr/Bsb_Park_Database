import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_URL = "http://localhost:8000"  # ajuste conforme sua API

st.set_page_config(page_title="Controle de Despesas", layout="wide")

# ------------------------------------------------------------
# REGISTRAR DESPESA
# ------------------------------------------------------------
def registrar_despesa():
    st.header("Registrar Despesa")

    funcionario = st.text_input("Nome do Funcionário")
    filial = st.text_input("Filial ID (ex: 01_SCS)")
    conta = st.selectbox("Conta", ["Operacional", "Administrativo", "Outros"])
    meio = st.selectbox("Meio de Pagamento", ["Dinheiro", "Pix", "Cartão", "Transferência"])
    recorrencia = st.selectbox("Recorrência", ["Fixa", "Extra"])
    valor = st.number_input("Valor da Despesa", min_value=0.0, step=0.01)

    # Seleção de ano e mês
    ano = st.number_input("Ano da Despesa", min_value=2020, max_value=2100, step=1, value=datetime.now().year)
    mes = st.number_input("Mês da Despesa", min_value=1, max_value=12, step=1, value=datetime.now().month)
    data_str = f"{ano}-{mes:02d}-01"

    if st.button("Registrar Despesa"):
        payload = {
            "funcionario": funcionario,
            "filial_id": filial,
            "conta": conta,
            "meio_de_pagamento": meio,
            "recorrencia": recorrencia,
            "valor": valor,
            "data": data_str
        }

        try:
            r = requests.post(f"{API_URL}/add", json=payload)
            if r.status_code == 200:
                st.success("Despesa registrada com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao registrar despesa.")
        except Exception as e:
            st.error(f"Erro ao conectar com API: {e}")

# ------------------------------------------------------------
# VISUALIZAR DESPESAS
# ------------------------------------------------------------
def visualizar_despesas():
    st.header("Visualizar Despesas")

    # Filtro mês/ano independente
    ano_filtro = st.number_input("Ano para buscar", min_value=2020, max_value=2100, step=1, value=datetime.now().year)
    mes_filtro = st.number_input("Mês para buscar", min_value=1, max_value=12, step=1, value=datetime.now().month)

    filtro_data = f"{ano_filtro}-{mes_filtro:02d}"

    try:
        r = requests.get(f"{API_URL}/all")
        if r.status_code != 200:
            st.error("Erro ao buscar despesas.")
            return

        data = r.json()
        df = pd.DataFrame(data)

        # filtrar pelo mês/ano
        df['data'] = pd.to_datetime(df['data'])
        df_filtrado = df[df['data'].dt.strftime('%Y-%m') == filtro_data]

        st.subheader(f"Despesas de {mes_filtro:02d}/{ano_filtro}")
        st.dataframe(df_filtrado, use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {e}")

# ------------------------------------------------------------
# APAGAR DESPESA
# ------------------------------------------------------------
def apagar_despesa():
    st.header("Apagar Despesa")

    cod = st.number_input("Código da despesa a apagar", min_value=1, step=1)

    if st.button("Apagar"):
        try:
            r = requests.delete(f"{API_URL}/delete/{cod}")
            if r.status_code == 200:
                st.success(f"Despesa {cod} apagada com sucesso.")
                st.rerun()
            else:
                st.error("Erro ao apagar despesa.")
        except Exception as e:
            st.error(f"Erro ao conectar com API: {e}")

# ------------------------------------------------------------
# MENU
# ------------------------------------------------------------
menu = st.sidebar.radio(
    "Menu", ["Registrar", "Visualizar", "Apagar"]
)

if menu == "Registrar":
    registrar_despesa()
elif menu == "Visualizar":
    visualizar_despesas()
elif menu == "Apagar":
    apagar_despesa()


