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

# --- Pegar lista de clientes filtrada ---
def get_clientes_filtrados():
    response = supabase.table("clientes") \
        .select("nome_cliente") \
        .eq("filial_id", "01_SCS") \
        .in_("tipo_de_cliente", ["Tickets_Convenio", "Rotativo"]) \
        .order("nome_cliente", ascending=True) \
        .execute()
    
    if response.error:
        st.error(f"Erro ao buscar clientes: {response.error.message}")
        return []
    else:
        return [cliente["nome_cliente"] for cliente in response.data]

clientes_lista = get_clientes_filtrados()

# --- FORMULÁRIO DE ENTRADA ---
st.subheader("Registrar nova entrada")
with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Cliente", clientes_lista)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)
    data_entrada = st.date_input("Data da entrada", value=datetime.now().date())
    submit_button = st.form_submit_button("Registrar entrada")

# Função para obter último ID (considerando id_entrada como serial no banco)
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", descending=True).limit(1).execute()
    if not response.data:
        return 0
    return response.data[0]["id_entrada"]

if submit_button:
    try:
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        # Buscar código do cliente baseado no nome e filial
        cliente_res = supabase.table("clientes") \
            .select("cod_mensalista") \
            .eq("nome_cliente", tipo_cliente) \
            .eq("filial_id", "01_SCS") \
            .execute()

        if cliente_res.error or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]

            # Combinar data_entrada (date) com hora atual para timestamp completo
            data_hora = datetime.combine(data_entrada, datetime.now().time()).isoformat()

            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": data_hora,
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas
            }).execute()

            if insert_response.error:
                st.error(f"Erro ao inserir no banco de dados: {insert_response.error.message}")
            else:
                st.success(f"Entrada registrada com sucesso! ID: {proximo_id}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")

# --- CONSULTA DE ENTRADAS POR DIA ---
st.subheader("Consultar entradas por data")

data_consulta = st.date_input("Selecione a data para consulta", value=datetime.now().date())
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

try:
    # Buscar entradas da filial 01_SCS
    # Para garantir que sejam só entradas do SCS, fazemos um join implícito buscando clientes da filial
    # Como supabase não tem join direto, precisamos buscar cod_cliente válidos na filial 01_SCS primeiro

    clientes_res = supabase.table("clientes") \
        .select("cod_mensalista") \
        .eq("filial_id", "01_SCS") \
        .execute()

    if clientes_res.error or not clientes_res.data:
        st.info("Nenhum cliente encontrado para a filial 01_SCS.")
        entradas_data = []
    else:
        cod_clientes_validos = [c["cod_mensalista"] for c in clientes_res.data]

        consulta = supabase.table("entradas") \
            .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada, cod_cliente") \
            .gte("data_entrada", inicio_dia) \
            .lte("data_entrada", fim_dia) \
            .in_("cod_cliente", cod_clientes_validos) \
            .order("data_entrada", ascending=False) \
            .execute()

        if consulta.error:
            st.error(f"Erro ao consultar entradas: {consulta.error.message}")
            entradas_data = []
        else:
            entradas_data = consulta.data

    if entradas_data:
        st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")

        # Mostrar entradas com botão para excluir
        for entrada in entradas_data:
            cliente = entrada["tipo_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")
            id_entrada = entrada["id_entrada"]

            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
            with col2:
                if st.button("Excluir", key=f"del_{id_entrada}"):
                    # Confirma exclusão
                    if st.confirm(f"Confirmar exclusão da entrada ID {id_entrada}?"):
                        delete_resp = supabase.table("entradas").delete().eq("id_entrada", id_entrada).execute()
                        if delete_resp.error:
                            st.error(f"Erro ao excluir: {delete_resp.error.message}")
                        else:
                            st.success(f"Entrada ID {id_entrada} excluída com sucesso.")
                            st.experimental_rerun()

        total_valor = sum(e["valor_entrada"] for e in entradas_data)
        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")

