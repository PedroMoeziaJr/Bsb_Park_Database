import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("📊 Visualização de Dados - BSB Park")

# Menu lateral com botões
tabela_opcao = st.sidebar.radio("Escolha a Tabela:", ["Clientes Cadastrados", "Caixas", "Despesas", "Estacionamentos"])

# --- CLIENTES ---
if tabela_opcao == "Clientes Cadastrados":
    st.header("📁 Clientes Cadastrados")

    # Obter filiais para filtro
    filiais_data = supabase.table("filiais").select("id, nome").execute()
    filiais_dict = {f["nome"]: f["id"] for f in filiais_data.data}
    filial_selecionada = st.sidebar.selectbox("Filtrar por Estacionamento", list(filiais_dict.keys()))

    id_filial = filiais_dict[filial_selecionada]

    resposta = supabase.table("clientes").select("*").eq("id_filial", id_filial).execute()
    if resposta.data:
        df = pd.DataFrame(resposta.data)
        st.dataframe(df)
    else:
        st.info("Nenhum cliente encontrado para essa filial.")

# --- ENTRADAS ---
elif tabela_opcao == "Caixas":
    st.header("💰 Caixas")

    data_filtro = st.sidebar.date_input("Filtrar por Data", value=datetime.now().date())

    inicio = datetime.combine(data_filtro, datetime.min.time()).isoformat()
    fim = datetime.combine(data_filtro, datetime.max.time()).isoformat()

    resposta = supabase.table("entradas") \
        .select("*") \
        .gte("data_entrada", inicio) \
        .lte("data_entrada", fim) \
        .order("data_entrada", desc=True) \
        .execute()

    if resposta.data:
        df = pd.DataFrame(resposta.data)
        df["data_entrada"] = pd.to_datetime(df["data_entrada"])
        df["hora"] = df["data_entrada"].dt.strftime("%H:%M:%S")
        st.dataframe(df)
        st.success(f"Total de entradas: {len(df)}")
    else:
        st.info("Nenhuma entrada encontrada nesta data.")

# --- DESPESAS ---
elif tabela_opcao == "Despesas":
    st.header("📉 Despesas")

    # Filtro por mês/ano
    hoje = datetime.today()
    ano = st.sidebar.selectbox("Ano", list(range(2023, hoje.year + 1)), index=(hoje.year - 2023))
    mes = st.sidebar.selectbox("Mês", list(range(1, 13)), index=(hoje.month - 1))

    resposta = supabase.table("despesas") \
        .select("*") \
        .eq("ano", ano) \
        .eq("mes", mes) \
        .order("dia", desc=True) \
        .execute()

    if resposta.data:
        df = pd.DataFrame(resposta.data)
        st.dataframe(df)
        total = df["valor"].astype(float).sum()
        st.success(f"Total de despesas em {mes:02d}/{ano}: R$ {total:.2f}")
    else:
        st.info("Nenhuma despesa registrada para este período.")

# --- FILIAIS ---
elif tabela_opcao == "Estacionamentos":
    st.header("🏢 Estacionamentos")

    resposta = supabase.table("filiais").select("*").execute()
    if resposta.data:
        df = pd.DataFrame(resposta.data)
        st.dataframe(df)
    else:
        st.info("Nenhuma filial encontrada.")

