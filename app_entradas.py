import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# --- Conexão com Supabase ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Caixa SCS")

# Lista de clientes (filial 01_SCS)
clientes_response = supabase.table("clientes").select("nome_cliente").eq("filial_id", "01_SCS").execute()
clientes_lista = [cliente["nome_cliente"] for cliente in clientes_response.data] if clientes_response.data else []

# --- FORMULÁRIO DE ENTRADA ---
st.subheader("Registrar nova entrada")
with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Cliente", clientes_lista)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)
    data_entrada_manual = st.date_input("Data da entrada", value=datetime.now().date())
    hora_entrada_manual = st.time_input("Hora da entrada", value=datetime.now().time())
    submit_button = st.form_submit_button("Registrar entrada")

# Função para obter último ID
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if not response or not response.data:
        return 20845
    return response.data[0]["id_entrada"]

# Registro no banco
if submit_button:
    try:
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        cliente_res = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", tipo_cliente).execute()
        if not cliente_res or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]
            data_completa = datetime.combine(data_entrada_manual, hora_entrada_manual).isoformat()

            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": data_completa,
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

# --- CONSULTA DE ENTRADAS POR DIA ---
st.subheader("Consultar entradas por data")

data_consulta = st.date_input("Selecione a data para consulta", value=datetime.now().date())
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

try:
    consulta = supabase.table("entradas") \
        .select("id_entrada, valor_entrada, forma_pagamento, qtd_entradas, data_entrada, clientes(nome_cliente, filial_id)") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    entradas_scs = [e for e in consulta.data if e["clientes"]["filial_id"] == "01_SCS"]

    if entradas_scs:
        total_valor = 0
        st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')} (SCS)")

        for entrada in entradas_scs:
            cliente = entrada["clientes"]["nome_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")
            entrada_id = entrada["id_entrada"]

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
            with col2:
                if st.button("🗑️ Excluir", key=f"del_{entrada_id}"):
                    supabase.table("entradas").delete().eq("id_entrada", entrada_id).execute()
                    st.warning(f"Entrada ID {entrada_id} excluída!")
                    st.experimental_rerun()

            total_valor += valor

        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data na filial SCS.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")
