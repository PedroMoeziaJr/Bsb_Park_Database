import streamlit as st
from supabase import create_client, Client
from datetime import date

# Inicializar conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("Caixa SCS")

# Obter o próximo id_entrada
try:
    resposta = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    ultimo_id = resposta.data[0]["id_entrada"] if resposta.data else 20845
    proximo_id = ultimo_id + 1
except Exception as e:
    st.error(f"Erro ao obter o último ID: {e}")
    proximo_id = 20846  # Valor padrão caso ocorra erro

# Obter lista de clientes
try:
    clientes_resposta = supabase.table("clientes").select("nome_cliente, cod_cliente").execute()
    clientes_data = clientes_resposta.data
    nomes_clientes = [cliente["nome_cliente"] for cliente in clientes_data]
    nome_cod_map = {cliente["nome_cliente"]: cliente["cod_cliente"] for cliente in clientes_data}
except Exception as e:
    st.error(f"Erro ao obter lista de clientes: {e}")
    nomes_clientes = []
    nome_cod_map = {}

# Formulário
with st.form("form_entrada"):
    st.subheader("Registrar Nova Entrada")

    st.markdown(f"**ID da Entrada:** {proximo_id}")
    data_entrada = date.today()
    st.markdown(f"**Data da Entrada:** {data_entrada.strftime('%d/%m/%Y')}")

    tipo_cliente = st.selectbox("Tipo de Cliente", nomes_clientes)

    forma_pagamento = st.selectbox("Forma de Pagamento", ["dinheiro", "cartão", "Apurado", "pix"])

    valor_entrada = st.number_input("Valor da Entrada", min_value=0.0, format="%.2f")

    qtd_entradas = st.number_input("Quantidade de Entradas", min_value=1, step=1)

    submit = st.form_submit_button("Registrar Entrada")

    if submit:
        if tipo_cliente in nome_cod_map:
            cod_cliente = nome_cod_map[tipo_cliente]
            nova_entrada = {
                "id_entrada": proximo_id,
                "data_entrada": data_entrada.isoformat(),
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas
            }
            try:
                resultado = supabase.table("entradas").insert(nova_entrada).execute()
                st.success("Entrada registrada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao registrar entrada: {e}")
        else:
            st.error("Cliente selecionado não encontrado na base de dados.")
