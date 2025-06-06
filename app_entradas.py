import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta

# Inicializa conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Caixa SCS")

# Função para obter lista de clientes filtrados conforme seu pedido
def get_clientes_filtrados():
    response = supabase.table("clientes") \
        .select("nome_cliente") \
        .eq("filial_id", "01_SCS") \
        .in_("tipo_de_cliente", ["Tickets_Convenio", "Rotativo"]) \
        .order("nome_cliente") \
        .execute()

    # Debug print para ver o retorno no log (remova depois)
    # print(response)

    if response is None:
        st.error("Erro na consulta: resposta nula")
        return []
    
    # Verifica status_code na resposta (exemplo da versão antiga)
    if "status_code" in response and response["status_code"] != 200:
        st.error(f"Erro na consulta: status {response['status_code']}")
        return []

    if "data" in response and response["data"]:
        return [cliente["nome_cliente"] for cliente in response["data"]]
    else:
        st.info("Nenhum cliente encontrado.")
        return []

# Carrega a lista de clientes para o selectbox
clientes_lista = get_clientes_filtrados()

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

# Função para obter último ID
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if response is None or not response.get("data"):
        return 20845
    return response["data"][0]["id_entrada"]

# Registro no banco
if submit_button:
    try:
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        cliente_res = supabase.table("clientes").select("cod_mensalista", "filial_id") \
            .eq("nome_cliente", tipo_cliente).execute()

        if cliente_res is None or not cliente_res.get("data"):
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res["data"][0]["cod_mensalista"]
            filial_id = cliente_res["data"][0]["filial_id"]

            # Garantir que só registre para filial 01_SCS
            if filial_id != "01_SCS":
                st.error("Cliente não pertence ao estacionamento SCS.")
            else:
                data_hora_entrada = datetime.combine(data_entrada, hora_entrada).isoformat()

                insert_response = supabase.table("entradas").insert({
                    "id_entrada": proximo_id,
                    "data_entrada": data_hora_entrada,
                    "tipo_cliente": tipo_cliente,
                    "cod_cliente": cod_cliente,
                    "forma_pagamento": forma_pagamento,
                    "valor_entrada": valor_entrada,
                    "qtd_entradas": qtd_entradas
                }).execute()

                if insert_response and insert_response.get("data"):
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
        .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .eq("filial_id", "01_SCS") \
        .order("data_entrada", desc=True) \
        .execute()

    if consulta and consulta.get("data"):
        st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
        total_valor = 0
        for entrada in consulta["data"]:
            id_entrada = entrada["id_entrada"]
            cliente = entrada["tipo_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")

            # Exibir com botão para excluir
            col1, col2 = st.columns([8,1])
            with col1:
                st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
            with col2:
                if st.button(f"Excluir {id_entrada}", key=f"del_{id_entrada}"):
                    delete_response = supabase.table("entradas").delete().eq("id_entrada", id_entrada).execute()
                    if delete_response and delete_response.get("status_code") == 204:
                        st.success(f"Entrada ID {id_entrada} excluída com sucesso.")
                        st.experimental_rerun()
                    else:
                        st.error("Erro ao excluir a entrada.")

            total_valor += valor

        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")
