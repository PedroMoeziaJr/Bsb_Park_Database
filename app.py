import streamlit as st
from supabase import create_client, Client
from datetime import date

# Dados do Supabase
SUPABASE_URL = "https://clyuxrlqbkdadhkpzaly.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"

# Conexão com o Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Cadastro de Despesa")

# Listas suspensas
filiais = [
    "01_SCS", "02_Taguatinga", "03_Ed_Prime", "04_504", "05_Rio_de_Janeiro",
    "06_Imperatriz_MA", "07_Itumbiara_GO", "08_Ituiutaba_MG", "09_Matriz",
    "10_PF_Ped_", "11_PF_CEL_"
]
pagamentos = ["Pix", "Internet", "Dda", "Boleto", "Transferencia"]
recorrencias = ["Extra", "Fixa"]

# Formulário
with st.form("form_despesa"):
    filial_id = st.selectbox("Filial", filiais)
    funcionario = st.text_input("Funcionário")
    valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01)
    meio_pagamento = st.selectbox("Meio de Pagamento", pagamentos)
    recorrencia = st.selectbox("Recorrência", recorrencias)
    submit = st.form_submit_button("Enviar")

    if submit:
        # Obter o próximo número sequencial
        dados = supabase.table("despesas").select("cod_pagamento").order("cod_pagamento", desc=True).limit(1).execute()
        if dados.data:
            ultimo_codigo = dados.data[0]["cod_pagamento"]
        else:
            ultimo_codigo = 100  # início

        proximo_codigo = ultimo_codigo + 1

        # Inserir novo registro
        nova_despesa = {
            "cod_pagamento": proximo_codigo,
            "data": date.today().isoformat(),
            "posto": filial_id,
            "funcionário": funcionario,
            "valor": valor,
            "meio de pagamento": meio_pagamento,
            "recorrência": recorrencia,
            "conta": ""  # pode ser preenchido depois
        }

        resultado = supabase.table("despesas").insert(nova_despesa).execute()

        if resultado.status_code == 201:
            st.success(f"Despesa registrada com sucesso! Código: {proximo_codigo}")
        else:
            st.error("Erro ao registrar despesa.")
