import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# Conexão com o Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Título
st.title("📊 Visualização de Dados - BSB Park")

# Barra lateral de navegação
st.sidebar.title("📁 Selecione uma Tabela")
opcao = st.sidebar.radio("Escolha uma opção:", ["Clientes Cadastrados", "Caixas", "Despesas", "Estacionamentos"])

# ----------------- CLIENTES -------------------
if opcao == "Clientes Cadastrados":
    st.subheader("👥 Clientes Cadastrados")

    # Filtro por filial
    filiais_data = supabase.table("filiais").select("id_filial, f_nome").execute()
    filiais_dict = {f["f_nome"]: f["id_filial"] for f in filiais_data.data}
    filial_selecionada_nome = st.selectbox("Filtrar por Estacionamento", list(filiais_dict.keys()))
    filial_id = filiais_dict[filial_selecionada_nome]

    clientes = supabase.table("clientes").select("*").eq("id_filial", filial_id).execute()

    if clientes.data:
        st.dataframe(clientes.data)
    else:
        st.info("Nenhum cliente encontrado para esta filial.")

# ----------------- CAIXAS -------------------
elif opcao == "Caixas":
    st.subheader("💰 Entradas (Caixa)")

    data_consulta = st.date_input("Selecione a data", value=datetime.now().date())
    inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
    fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

    entradas = supabase.table("entradas") \
        .select("tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    if entradas.data:
        st.dataframe(entradas.data)
        total = sum(item["valor_entrada"] for item in entradas.data)
        st.success(f"💵 Total do dia: R$ {total:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

# ----------------- DESPESAS -------------------
elif opcao == "Despesas":
    st.subheader("📉 Despesas")

    meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    mes_nome = st.selectbox("Selecione o mês", list(meses.keys()))
    mes = meses[mes_nome]
    ano = datetime.now().year

    inicio_mes = datetime(ano, mes, 1).isoformat()
    fim_mes = (datetime(ano, mes, 28) + timedelta(days=4)).replace(day=1) - timedelta(seconds=1)
    fim_mes = fim_mes.isoformat()

    despesas = supabase.table("despesas") \
        .select("*") \
        .gte("data_despesa", inicio_mes) \
        .lte("data_despesa", fim_mes) \
        .order("data_despesa", desc=True) \
        .execute()

    if despesas.data:
        st.dataframe(despesas.data)
        total_despesas = sum(item["valor_despesa"] for item in despesas.data)
        st.error(f"📉 Total de despesas no mês: R$ {total_despesas:.2f}")
    else:
        st.info("Nenhuma despesa encontrada para este mês.")

# ----------------- FILIAIS -------------------
elif opcao == "Estacionamentos":
    st.subheader("🏢 Estacionamentos (Filiais)")
    filiais = supabase.table("filiais").select("*").execute()

    if filiais.data:
        st.dataframe(filiais.data)
    else:
        st.info("Nenhuma filial encontrada.")

