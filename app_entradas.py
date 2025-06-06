import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Inicializa conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Caixa SCS")

# Função para buscar clientes filtrados pelo tipo_de_cliente
def get_clientes_filtrados():
    response = supabase.table("clientes") \
        .select("nome_cliente") \
        .in_("tipo_de_cliente", ["Tickets_Convenio", "Rotativo"]) \
        .order("nome_cliente") \
        .execute()

    if response is None or "data" not in response:
        st.error("Erro ao buscar clientes")
        return []

    return [cliente["nome_cliente"] for cliente in response["data"]]

clientes_lista = get_clientes_filtrados()

# --- FORMULÁRIO DE ENTRADA ---
st.subheader("Registrar nova entrada")
with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Escolha o cliente", clientes_lista)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)
    data_entrada = st.date_input("Data da entrada", value=datetime.now().date())
    submit_button = st.form_submit_button("Registrar entrada")

# Função para obter último ID
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if not response or not response.data:
        return 20845
    return response.data[0]["id_entrada"]

if submit_button:
    try:
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        # Buscar código do cliente com base no nome selecionado
        cliente_res = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", tipo_cliente).execute()
        if not cliente_res or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]

            # Inserir entrada no banco
            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": datetime.combine(data_entrada, datetime.now().time()).isoformat(),
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas
            }).execute()

            if insert_response.data:
                st.success(f"Entrada registrada com sucesso! ID: {proximo_id}")
            else:
                st.error("Erro ao inserir no banco de dados.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")

