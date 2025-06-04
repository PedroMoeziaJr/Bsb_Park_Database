import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Configurações do Supabase
SUPABASE_URL = "https://clxuxrlqbkdadhkpzaly.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# Formulário
with st.form("form_despesa"):
    filial = st.selectbox("Filial", filiais)
    funcionario = st.text_input("Funcionário")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    meio_pagamento = st.selectbox("Meio de Pagamento", meios_pagamento)
    recorrencia = st.selectbox("Recorrência", recorrencias)
    conta = st.selectbox("Conta", contas)

    submitted = st.form_submit_button("Enviar")

    if submitted:
        # Obter último cod_pagamento
        dados = supabase.table("despesas")\
            .select("cod_pagamento")\
            .order("cod_pagamento", desc=True)\
            .limit(1)\
            .execute()

        ultimo_cod = dados.data[0]["cod_pagamento"] if dados.data else 100
        novo_cod = ultimo_cod + 1

        nova_despesa = {
            "cod_pagamento": novo_cod,
            "data": datetime.today().date().isoformat(),
            "filial_id": filial,
            "funcionario": funcionario,
            "valor": valor,
            "meio_de_pagamento": meio_pagamento,
            "recorrencia": recorrencia,
            "conta": conta
        }

        try:
            resultado = supabase.table("despesas").insert(nova_despesa).execute()
            st.success("Despesa registrada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao registrar despesa: {e}")



st.markdown("---")
st.header("Visualização de Despesas")

# Buscar todos os dados da tabela
try:
    resposta = supabase.table("despesas").select("*").execute()
    df = resposta.data

    if df:
        import pandas as pd

        # Converter para DataFrame
        df = pd.DataFrame(df)
        df["data"] = pd.to_datetime(df["data"])

        # Filtros
        anos = sorted(df["data"].dt.year.unique(), reverse=True)
        meses = sorted(df["data"].dt.month.unique())

        col1, col2 = st.columns(2)
        with col1:
            ano_selecionado = st.selectbox("Ano", anos)
        with col2:
            mes_selecionado = st.selectbox("Mês", meses)

        # Aplicar filtros
        df_filtrado = df[
            (df["data"].dt.year == ano_selecionado) &
            (df["data"].dt.month == mes_selecionado)
        ]

        st.dataframe(
            df_filtrado.sort_values(by="data", ascending=False).reset_index(drop=True),
            use_container_width=True
        )

    else:
        st.info("Nenhuma despesa registrada ainda.")
except Exception as e:
    st.error(f"Erro ao buscar dados: {e}")

