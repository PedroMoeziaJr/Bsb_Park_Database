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

st.title("Consulta de Entradas por Dia")

# Campo para selecionar a data
data_consulta = st.date_input("Selecione a data para consulta", value=datetime.now().date())

# Converte para intervalo de data/hora
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

# Realiza a consulta no banco
try:
    consulta = supabase.table("entradas") \
        .select("tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .gte("data_entrada", inicio_dia) \
        .lte("data_entrada", fim_dia) \
        .order("data_entrada", desc=True) \
        .execute()

    if consulta.data:
        st.subheader(f"Entradas em {data_consulta.strftime('%d/%m/%Y')}")
        
        total_valor = 0
        for entrada in consulta.data:
            cliente = entrada["tipo_cliente"]
            valor = entrada["valor_entrada"]
            pagamento = entrada["forma_pagamento"]
            qtd = entrada["qtd_entradas"]
            data_hora = datetime.fromisoformat(entrada["data_entrada"]).strftime("%H:%M:%S")

            st.markdown(f"- **{cliente}** | R$ {valor:.2f} | {pagamento} | Qtd: {qtd} | Hora: {data_hora}")
            total_valor += valor

        st.success(f"💰 Total do dia: R$ {total_valor:.2f}")
    else:
        st.info("Nenhuma entrada encontrada para esta data.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")
