import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Função para iniciar conexão com Supabase
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("Visualização Simples dos Dados")

# Sidebar com opções
opcao = st.sidebar.radio("Selecione a tabela para visualizar:", 
                         ["Clientes Cadastrados", "Caixas", "Despesas", "Estacionamentos"])

if opcao == "Estacionamentos":
    # Consulta filiais
    filiais_data = supabase.table("filiais").select("id_filial, f_nome").execute()
    st.subheader("Estacionamentos (Filiais)")
    st.dataframe(filiais_data.data)

elif opcao == "Clientes Cadastrados":
    # Pega filiais para filtro
    filiais = supabase.table("filiais").select("id_filial, f_nome").execute()
    filiais_options = {f["f_nome"]: f["id_filial"] for f in filiais.data}

    filial_selecionada = st.selectbox("Escolha o estacionamento (filial):", options=list(filiais_options.keys()))

    if filial_selecionada:
        filial_id = filiais_options[filial_selecionada]
        clientes = supabase.table("clientes") \
            .select("*") \
            .eq("cod_estacionamento", filial_id) \
            .execute()
        st.subheader(f"Clientes Cadastrados - {filial_selecionada}")
        st.dataframe(clientes.data)

elif opcao == "Caixas":
    dia = st.date_input("Selecione o dia:", datetime.now())
    dia_str = dia.strftime("%Y-%m-%d")

    entradas = supabase.table("entradas") \
        .select("*") \
        .eq("data_entrada", dia_str) \
        .execute()

    st.subheader(f"Caixas do dia {dia_str}")
    st.dataframe(entradas.data)

elif opcao == "Despesas":
    mes = st.slider("Selecione o mês:", 1, 12, datetime.now().month)
    ano = st.number_input("Selecione o ano:", min_value=2000, max_value=2100, value=datetime.now().year)

    inicio_mes = f"{ano}-{mes:02d}-01"
    fim_mes = f"{ano}-{mes:02d}-31"  # simplificação para pegar todo o mês

    despesas = supabase.table("despesas") \
        .select("*") \
        .gte("data", inicio_mes) \
        .lte("data", fim_mes) \
        .order("data", desc=True) \
        .execute()

    st.subheader(f"Despesas de {mes:02d}/{ano}")
    st.dataframe(despesas.data)
