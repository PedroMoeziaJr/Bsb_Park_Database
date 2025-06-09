import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

# Configuração do Supabase
url = "https://clxuxrlqbkdadhkpzaly.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"
supabase: Client = create_client(url, key)

st.title("Folha de Pagamento")

# Buscar funcionários
response = supabase.table("funcionario").select("id_funcionario, nome_funcionario").execute()

if response.data:
    funcionarios = pd.DataFrame(response.data)

    # Lista suspensa com nome dos funcionários
    funcionario_nome = st.selectbox("Selecione o Funcionário", funcionarios["nome_funcionario"])
    funcionario_id = funcionarios.loc[funcionarios["nome_funcionario"] == funcionario_nome, "id_funcionario"].values[0]

    # Selecionar data de pagamento
    data_pagamento = st.date_input("Data de Pagamento", value=date.today())

    # Tipo de lançamento: provento ou desconto
    provento_desconto = st.selectbox("Provento ou Desconto", ["provento", "desconto"])

    # Nome do lançamento
    tipo = st.text_input("Descrição do Lançamento")

    # Valor do lançamento
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")

    # Botão para salvar
    if st.button("Salvar Lançamento"):
        data = {
            "id_funcionario": funcionario_id,
            "data_pagamento": data_pagamento.isoformat(),
            "provento_desconto": provento_desconto,
            "tipo": tipo,
            "valor": valor
        }
        result = supabase.table("folha_pagamento").insert(data).execute()

        if result.status_code == 201:
            st.success("Lançamento registrado com sucesso!")
        else:
            st.error("Erro ao registrar lançamento.")
else:
    st.warning("Nenhum funcionário cadastrado.")
