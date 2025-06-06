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

# Função para obter lista de clientes filtrados (tipo_de_cliente = Tickets_Convenio ou Rotativo e filial_id = 01_SCS)
def get_clientes_filtrados():
    response = supabase.table("clientes") \
        .select("nome_cliente") \
        .eq("filial_id", "01_SCS") \
        .in_("tipo_de_cliente", ["Tickets_Convenio", "Rotativo"]) \
        .order("nome_cliente") \
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
    if not response or not response.data:
        return 20845
    return response.data[0]["id_entrada"]

# Registro no banco
if submit_button:
    try:
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        # Busca cod_mensalista do cliente selecionado
        cliente_res = supabase.table("clientes") \
            .select("cod_mensalista") \
            .eq("nome_cliente", tipo_cliente) \
            .eq("filial_id", "01_SCS") \
            .execute()

        if not cliente_res or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]

            # Combina data e hora escolhidas para datetime completo
            data_hora_entrada = datetime.combine(data_entrada, hora_entrada)

            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": data_hora_entrada.isoformat(),
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
    # Consulta entradas do estacionamento SCS (filial_id = '01_SCS') só para clientes que estejam nessa filial
    consulta = supabase.table("entradas") \
        .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada, cod_cliente") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    if consulta.data:
        # Filtra entradas para clientes que estejam em '01_SCS' via relacionamento com tabela clientes
        cod_clientes_scs = [c['cod_mensalista'] for c in supabase.table("clientes").select("cod_mensalista").eq("filial_id", "01_SCS").execute().data]

        entradas_scs = [e for e in consulta.data if e["cod_cliente"] in cod_clientes_scs]

        if entradas_scs:
            st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
            total_valor = 0
            for entrada in entradas_scs:
                cliente = entrada["tipo_cliente"]
                valor = entrada["valor_entrada"]
                pagamento = entrada["forma_pagamento"]
                qtd = entrada["qtd_entradas"]
                data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")
                id_entrada = entrada["id_entrada"]

                st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora} | ID: {id_entrada}")

            # Botão para excluir uma entrada por ID
            id_para_excluir = st.number_input("Digite o ID da entrada para excluir", min_value=0, step=1)
            if st.button("Excluir entrada"):
                if id_para_excluir:
                    delete_response = supabase.table("entradas").delete().eq("id_entrada", id_para_excluir).execute()
                    if delete_response.error:
                        st.error(f"Erro ao excluir entrada: {delete_response.error.message}")
                    else:
                        st.success(f"Entrada com ID {id_para_excluir} excluída com sucesso!")
                        st.experimental_rerun()

            total_valor = sum(e["valor_entrada"] for e in entradas_scs)
            st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
        else:
            st.info("Nenhuma entrada encontrada para esta data no estacionamento SCS.")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")

