import streamlit as st
from supabase import create_client, Client
from datetime import datetime, time

# Inicializa conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Caixa 01_SCS")

# Lista de clientes limitados para o SCS
clientes_lista = [
    "Atlantico Engenharia Ltda",
    "Cliente Rotativo Scs",
    "Bradesco Agencia 0606",
    "N&N Ass. E Cons Empresarial",
    "Bradesco S.A Dcps Varejo",
    "Bradesco Prime",
    "Bradesco Empresas",
    "Centro Auditivo Telex",
    "Top Tier",
    "Relações Institucionais",
    "Paulus Livraria",
    "Conselho Regional De Economia",
    "Atlantico Engenharia Ltda",
    "Maira Cantieri Silveira Vieira"
]

# --- FORMULÁRIO DE ENTRADA ---
st.subheader("Registrar nova entrada")
with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Tipo de cliente", clientes_lista)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)
    data_entrada = st.date_input("Data da entrada", value=datetime.now().date())
    hora_entrada = st.time_input("Hora da entrada", value=datetime.now().time())
    submit_button = st.form_submit_button("Registrar entrada")

def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if not response or not response.data:
        return 20845
    return response.data[0]["id_entrada"]

if submit_button:
    try:
        # Combina data e hora
        data_hora_entrada = datetime.combine(data_entrada, hora_entrada)

        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        # Busca código do cliente
        cliente_res = supabase.table("clientes") \
            .select("cod_mensalista") \
            .eq("nome_cliente", tipo_cliente) \
            .execute()

        if not cliente_res or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]

            # Insere a entrada com id_filial fixo para SCS
            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": data_hora_entrada.isoformat(),
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas,
                "id_filial": "01_SCS"
            }).execute()

            if insert_response.data:
                st.success(f"Entrada registrada com sucesso! ID: {proximo_id}")
            else:
                st.error("Erro ao inserir no banco de dados.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")

# --- CONSULTA DE ENTRADAS POR DIA ---
st.subheader("Consultar suas entradas por data")

data_consulta = st.date_input("Selecione a data para consulta", value=datetime.now().date())
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

try:
    consulta = supabase.table("entradas") \
        .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .eq("id_filial", "01_SCS") \
        .eq("tipo_cliente", st.session_state.get("usuario_tipo_cliente", "")) \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    if consulta.data:
        st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
        total_valor = 0
        for entrada in consulta.data:
            cliente = entrada["tipo_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")
            entrada_id = entrada["id_entrada"]

            st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora} | ID: {entrada_id}")
            total_valor += valor

        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")
