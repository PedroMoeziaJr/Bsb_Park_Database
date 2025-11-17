import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
import requests

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

# -------------------------------
# FORMULÁRIO
# -------------------------------
with st.form("form_despesa"):
    filial = st.selectbox("Filial", filiais)
    funcionario = st.text_input("Funcionário")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    meio_pagamento = st.selectbox("Meio de Pagamento", meios_pagamento)
    recorrencia = st.selectbox("Recorrência", recorrencias)
    conta = st.selectbox("Conta", contas)
    data_escolhida = st.date_input("Data da Despesa", datetime.today().date())

    submitted = st.form_submit_button("Enviar")

    if submitted:
        dados = supabase.table("despesas") \
            .select("cod_pagamento") \
            .order("cod_pagamento", desc=True) \
            .limit(1) \
            .execute()

        ultimo_cod = dados.data[0]["cod_pagamento"] if dados.data else 100
        novo_cod = ultimo_cod + 1

        nova_despesa = {
            "cod_pagamento": novo_cod,
            "data": data_escolhida.isoformat(),
            "filial_id": filial,
            "funcionario": funcionario,
            "valor": valor,
            "meio_de_pagamento": meio_pagamento,
            "recorrencia": recorrencia,
            "conta": conta
        }

        try:
            supabase.table("despesas").insert(nova_despesa).execute()
            st.success("Despesa registrada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao registrar despesa: {e}")

# -------------------------------
# VISUALIZAÇÃO DE DESPESAS
# -------------------------------
st.markdown("---")
st.header("Visualização de Despesas")

mes = st.selectbox("Selecione o mês", list(range(1, 13)), format_func=lambda m: f"{m:02d}")
ano = st.number_input("Selecione o ano", min_value=2020, max_value=2100, value=datetime.today().year)

mes_str = f"{ano}-{mes:02d}"  # YYYY-MM

try:
    resposta = supabase.table("despesas").select("*").execute()
    df = resposta.data

    if df:
        df = pd.DataFrame(df)
        df["data"] = pd.to_datetime(df["data"])
        df_filtrado = df[df["data"].dt.strftime("%Y-%m") == mes_str]

        st.subheader(f"Despesas de {mes_str}")
        st.dataframe(df_filtrado)

        st.subheader("Apagar Despesa")
        for _, row in df_filtrado.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 **{row['cod_pagamento']}** — R$ {row['valor']:.2f} — {row['funcionario']}")
            with col2:
                if st.button("Apagar", key=f"del_{row['cod_pagamento']}"):
                    delete_url = f"{SUPABASE_URL}/rest/v1/despesas?cod_pagamento=eq.{row['cod_pagamento']}"
                    headers = {
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    }
                    response = requests.delete(delete_url, headers=headers)

                    if response.status_code == 204:
                        st.success(f"Despesa {row['cod_pagamento']} apagada.")
                        st.rerun()
                    else:
                        st.error("Erro ao apagar despesa.")

    else:
        st.info("Nenhuma despesa registrada.")

except Exception as e:
    st.error(f"Erro ao carregar despesas: {e}")


