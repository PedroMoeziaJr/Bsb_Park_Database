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

# Busca clientes do tipo Tickets_Convenio ou Rotativo
def get_clientes_filtrados():
    response = supabase.table("clientes") \
        .select("nome_cliente, tipo_de_cliente, filial_id") \
        .in_("tipo_de_cliente", ["Tickets_Convenio", "Rotativo"]) \
        .eq("filial_id", "01_SCS") \
        .order("nome_cliente", ascending=True) \
        .execute()
    
    if response.error:
        st.error(f"Erro ao buscar clientes: {response.error}")
        return []
    if response.data:
        return [cliente["nome_cliente"] for cliente in response.data]
    return []

clientes_lista = get_clientes_filtrados()

if not clientes_lista:
    st.warning("Nenhum cliente encontrado para seleção.")
else:
    # --- FORMULÁRIO DE ENTRADA ---
    st.subheader("Registrar nova entrada")
    with st.form("form_entrada"):
        tipo_cliente = st.selectbox("Cliente", clientes_lista)
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
            ultimo_id = get_last_id()
            proximo_id = ultimo_id + 1

            # Busca código do cliente e filial_id para garantir filtro
            cliente_res = supabase.table("clientes") \
                .select("cod_mensalista, filial_id") \
                .eq("nome_cliente", tipo_cliente) \
                .eq("filial_id", "01_SCS") \
                .execute()

            if not cliente_res or not cliente_res.data:
                st.error("Código do cliente não encontrado ou cliente não pertence à filial SCS.")
            else:
                cod_cliente = cliente_res.data[0]["cod_mensalista"]
                # Combina data e hora selecionados
                dt_entrada = datetime.combine(data_entrada, hora_entrada)

                insert_response = supabase.table("entradas").insert({
                    "id_entrada": proximo_id,
                    "data_entrada": dt_entrada.isoformat(),
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
            .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada, cod_cliente") \
            .gte("data_entrada", inicio_dia) \
            .lte("data_entrada", fim_dia) \
            .order("data_entrada", desc=True) \
            .execute()

        # Filtra só entradas cujo cliente está na filial 01_SCS
        # Para isso, buscar clientes SCS e filtrar localmente:
        clientes_scs_res = supabase.table("clientes") \
            .select("cod_mensalista") \
            .eq("filial_id", "01_SCS") \
            .execute()
        clientes_scs = set(c["cod_mensalista"] for c in clientes_scs_res.data) if clientes_scs_res.data else set()

        if consulta.data:
            st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
            total_valor = 0
            entradas_exibidas = []
            for entrada in consulta.data:
                if entrada["cod_cliente"] not in clientes_scs:
                    continue
                entradas_exibidas.append(entrada)

            if not entradas_exibidas:
                st.info("Nenhuma entrada encontrada para esta data e filial SCS.")
            else:
                for entrada in entradas_exibidas:
                    cliente = entrada["tipo_cliente"]
                    valor = entrada["valor_entrada"]
                    pagamento = entrada["forma_pagamento"]
                    qtd = entrada["qtd_entradas"]
                    data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")
                    id_entrada = entrada["id_entrada"]

                    # Linha com botão para excluir a entrada
                    col1, col2 = st.columns([8,1])
                    with col1:
                        st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
                    with col2:
                        if st.button("Excluir", key=f"excluir_{id_entrada}"):
                            del_response = supabase.table("entradas").delete().eq("id_entrada", id_entrada).execute()
                            if del_response.error:
                                st.error(f"Erro ao excluir entrada ID {id_entrada}: {del_response.error}")
                            else:
                                st.success(f"Entrada ID {id_entrada} excluída com sucesso.")
                                st.experimental_rerun()

                    total_valor += valor
                st.success(f"💰 Total do dia: R$ {total_valor:.2f}")

        else:
            st.info("Nenhuma entrada encontrada para esta data.")

    except Exception as e:
        st.error(f"Erro ao consultar entradas: {e}")
