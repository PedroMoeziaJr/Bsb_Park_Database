import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime
import pandas as pd

# Configurações do Supabase
SUPABASE_URL = "https://clxuxrlqbkdadhkpzaly.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Registro de Despesas", layout="wide")
st.title("Registro de Despesas")

# Listas suspensas
filiais = [
    "01_SCS", "02_Taguatinga", "03_Ed_Prime", "04_504",
    "05_Rio_de_Janeiro", "06_Imperatriz_MA", "07_Itumbiara_GO",
    "08_Ituiutaba_MG", "09_Matriz", "10_PF_Ped_", "11_PF_CEL_"
]

meios_pagamento = ['Pix', 'Internet', 'Dda', 'Boleto', 'Transferencia']
recorrencias = ['Extra', 'Fixa']

contas = [
    "Operacional", "Vale Refeição", "Vale Transporte", "Salário", "Bancária",
    "Energia", "Recursos Humanos", "Internet_Telefone", "Condomínio",
    "Tributo", "Pessoal", "Contabil_Jurídica", "Outro"
]

# --------------------------
# FORMULÁRIO DE DESPESAS
# --------------------------
with st.form("form_despesa"):
    c1, c2 = st.columns(2)
    with c1:
        filial = st.selectbox("Filial", filiais)
        funcionario = st.text_input("Funcionário")
        conta = st.selectbox("Conta", contas)
    with c2:
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        meio_pagamento = st.selectbox("Meio de Pagamento", meios_pagamento)
        recorrencia = st.selectbox("Recorrência", recorrencias)

    data_registro = st.date_input("Data da Despesa (registro)", date.today())

    submitted = st.form_submit_button("Enviar")

    if submitted:
        # Obter último cod_pagamento
        try:
            dados = supabase.table("despesas")\
                .select("cod_pagamento")\
                .order("cod_pagamento", desc=True)\
                .limit(1).execute()

            try:
                ultimo_cod = int(dados.data[0]["cod_pagamento"])
            except:
                ultimo_cod = 100

        except Exception:
            ultimo_cod = 100

        novo_cod = ultimo_cod + 1

        nova_despesa = {
            "cod_pagamento": str(novo_cod),  # <-- garantir compatibilidade
            "data": data_registro.isoformat(),
            "filial_id": filial,
            "funcionario": funcionario,
            "valor": float(valor),
            "meio_de_pagamento": meio_pagamento,
            "recorrencia": recorrencia,
            "conta": conta
        }

        try:
            supabase.table("despesas").insert(nova_despesa).execute()
            st.success("Despesa registrada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao registrar despesa: {e}")

st.markdown("---")

# --------------------------
# VISUALIZAÇÃO (BUSCA DADOS)
# --------------------------
st.header("Visualização de Despesas")

try:
    resposta = supabase.table("despesas").select("*").execute()
    registros = resposta.data if resposta.data else []
except Exception as e:
    st.error(f"Erro ao buscar despesas: {e}")
    registros = []

# DataFrame
if registros:
    df_all = pd.DataFrame(registros)
    df_all["data"] = pd.to_datetime(df_all["data"], errors="coerce")
    df_all = df_all.dropna(subset=["data"])
else:
    df_all = pd.DataFrame(columns=[
        "cod_pagamento", "data", "filial_id", "funcionario",
        "valor", "meio_de_pagamento", "recorrencia", "conta"
    ])

# --------------------------
# FILTRO MÊS/ANO
# --------------------------
col_filter_1, col_filter_2, col_filter_3 = st.columns([2,2,1])
with col_filter_1:
    meses = [
        "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril",
        "05 - Maio", "06 - Junho", "07 - Julho", "08 - Agosto",
        "09 - Setembro", "10 - Outubro", "11 - Novembro", "12 - Dezembro"
    ]
    mes_idx = st.selectbox("Mês (filtrar)", options=list(range(1,13)),
                           format_func=lambda x: meses[x-1],
                           index=date.today().month-1)

with col_filter_2:
    if not df_all.empty:
        anos_disponiveis = sorted(df_all["data"].dt.year.unique().tolist(), reverse=True)
    else:
        anos_disponiveis = [date.today().year]

    ano_idx = st.selectbox("Ano (filtrar)", anos_disponiveis)

with col_filter_3:
    st.write("")
    if st.button("Atualizar"):
        st.experimental_rerun()

# Filtra
df_filtrado = df_all[
    (df_all["data"].dt.month == mes_idx) &
    (df_all["data"].dt.year == ano_idx)
]

st.subheader(f"Despesas {mes_idx:02d}/{ano_idx} — {len(df_filtrado)} registros")

# --------------------------
# TABELA + APAGAR
# --------------------------
if df_filtrado.empty:
    st.info("Nenhuma despesa encontrada.")
else:

    header_cols = st.columns([1.2, 1.8, 1.6, 1.2, 1.4, 2.8, 1.0])
    header_cols[0].write("**Código**")
    header_cols[1].write("**Data**")
    header_cols[2].write("**Filial**")
    header_cols[3].write("**Valor**")
    header_cols[4].write("**Pagamento**")
    header_cols[5].write("**Funcionário**")
    header_cols[6].write("**Ação**")

    for _, row in df_filtrado.sort_values("data", ascending=False).iterrows():

        cod_pg = str(row["cod_pagamento"])  # <-- agora garantido como string

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2, 1.8, 1.6, 1.2, 1.4, 2.8, 1.0])

        col1.write(cod_pg)
        col2.write(row["data"].date().isoformat())
        col3.write(row.get("filial_id", ""))
        col4.write(f"R$ {float(row.get('valor', 0)):,.2f}")
        col5.write(row.get("meio_de_pagamento", ""))
        col6.write(row.get("funcionario", ""))

        if col7.button("Apagar", key=f"del_{cod_pg}"):

            try:
                resposta = supabase.table("despesas").delete().eq("cod_pagamento", cod_pg).execute()

                st.write("DEBUG DELETE:", resposta)

                st.success(f"Despesa {cod_pg} apagada.")
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Erro ao apagar: {e}")


# RESUMO TOTAL DO MÊS
if not df_filtrado.empty:
    total_mes = df_filtrado["valor"].astype(float).sum()
    st.metric("Total do mês (R$)", f"R$ {total_mes:,.2f}")

