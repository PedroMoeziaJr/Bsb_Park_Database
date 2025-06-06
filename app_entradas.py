import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Conexão com o Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("📊 Visualização de Dados do Estacionamento")

# Menu lateral
opcao = st.sidebar.radio("Escolha a Tabela", ["Clientes Cadastrados", "Caixas", "Despesas", "Estacionamentos"])

# 🔹 Estacionamentos (filiais)
if opcao == "Estacionamentos":
    st.subheader("📍 Estacionamentos Cadastrados")
    try:
        filiais = supabase.table("filiais").select("id_filial, f_nome").execute()
        st.dataframe(pd.DataFrame(filiais.data))
    except Exception as e:
        st.error(f"Erro ao carregar filiais: {e}")

# 🔹 Clientes Cadastrados
elif opcao == "Clientes Cadastrados":
    st.subheader("👤 Clientes Cadastrados")
    try:
        filiais = supabase.table("filiais").select("id_filial, f_nome").execute()
        filiais_opcoes = {f["f_nome"]: f["id_filial"] for f in filiais.data}
        nome_filial = st.selectbox("Selecione o Estacionamento", list(filiais_opcoes.keys()))
        id_filial = filiais_opcoes[nome_filial]

        try:
            clientes = supabase.table("clientes") \
                .select("*") \
                .eq("cod_estacionamento", id_filial) \
                .execute()
            st.dataframe(pd.DataFrame(clientes.data))
        except Exception as e:
            st.error(f"Erro ao buscar clientes: {e}")
    except Exception as e:
        st.error(f"Erro ao carregar lista de filiais: {e}")

# 🔹 Caixas (entradas)
elif opcao == "Caixas":
    st.subheader("💰 Movimentação de Caixa")
    data_caixa = st.date_input("Selecione a Data")
    try:
        entradas = supabase.table("entradas") \
            .select("*") \
            .like("data_entrada", f"{data_caixa}%" ) \
            .execute()
        st.dataframe(pd.DataFrame(entradas.data))
    except Exception as e:
        st.error(f"Erro ao buscar entradas: {e}")

# 🔹 Despesas
elif opcao == "Despesas":
    st.subheader("💸 Despesas")
    mes = st.selectbox("Selecione o mês", [
        "01", "02", "03", "04", "05", "06",
        "07", "08", "09", "10", "11", "12"
    ])
    try:
        despesas = supabase.table("despesas") \
            .select("*") \
            .like("data", f"2024-{mes}-%") \
            .execute()
        st.dataframe(pd.DataFrame(despesas.data))
    except Exception as e:
        st.error(f"Erro ao buscar despesas: {e}")
