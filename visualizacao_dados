import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Conexão com o Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("📊 Visualização de Entradas")

# --- Filtros ---
st.sidebar.header("Filtros")
data_consulta = st.sidebar.date_input("Data", value=datetime.now().date())

# Consulta todos os clientes disponíveis
clientes_data = supabase.table("entradas").select("tipo_cliente").execute()
clientes_unicos = sorted(set(e["tipo_cliente"] for e in clientes_data.data))
cliente_filtro = st.sidebar.selectbox("Cliente (opcional)", ["Todos"] + clientes_unicos)

# Consulta ao banco com base na data
inicio_dia = datetime.combine(data_consulta, datetime.min.time()).isoformat()
fim_dia = datetime.combine(data_consulta, datetime.max.time()).isoformat()

query = supabase.table("entradas") \
    .select("tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
    .gte("data_entrada", inicio_dia) \
    .lte("data_entrada", fim_dia)

if cliente_filtro != "Todos":
    query = query.eq("tipo_cliente", cliente_filtro)

resposta = query.order("data_entrada", desc=True).execute()

# --- Exibição dos dados ---
if resposta.data:
    df = pd.DataFrame(resposta.data)
    df["data_entrada"] = pd.to_datetime(df["data_entrada"])
    df["hora"] = df["data_entrada"].dt.strftime("%H:%M:%S")
    df["valor_entrada"] = df["valor_entrada"].astype(float)

    st.markdown(f"### Entradas em {data_consulta.strftime('%d/%m/%Y')}")
    st.dataframe(df[["tipo_cliente", "valor_entrada", "forma_pagamento", "qtd_entradas", "hora"]])

    total = df["valor_entrada"].sum()
    st.success(f"💰 Total do dia: R$ {total:.2f}")

    # Exportação
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar como CSV",
        data=csv,
        file_name=f"entradas_{data_consulta}.csv",
        mime='text/csv'
    )
else:
    st.warning("Nenhuma entrada encontrada para os filtros selecionados.")
