import streamlit as st
from supabase import create_client, Client
import os

# Configuração do Supabase - substitua pelas suas variáveis
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

st.title("Folha de Pagamento")

# Buscar funcionários para dropdown
funcionarios = supabase.table("funcionario").select("id_funcionario, nome_funcionario").execute()

if funcionarios.error:
    st.error("Erro ao carregar funcionários")
    st.stop()

lista_funcionarios = funcionarios.data

# Mapeamento id->nome e lista para dropdown
id_nome_map = {f["id_funcionario"]: f["nome_funcionario"] for f in lista_funcionarios}
nomes_funcionarios = [f["nome_funcionario"] for f in lista_funcionarios]

# Selecione funcionário pelo nome e encontre o id
nome_selecionado = st.selectbox("Funcionário", nomes_funcionarios)
id_funcionario_selecionado = next(key for key, value in id_nome_map.items() if value == nome_selecionado)

# Data de pagamento
data_pagamento = st.date_input("Data do pagamento")

# Tipo provento ou desconto
provento_desconto = st.selectbox("Provento ou Desconto", ["provento", "desconto"])

# Campo para tipo
tipo = st.text_input("Descrição (tipo)")

# Campo para valor
valor = st.number_input("Valor", min_value=0.0, format="%.2f")

if st.button("Lançar na Folha"):
    if not tipo:
        st.warning("Preencha a descrição (tipo).")
    else:
        # Converter data para string 'YYYY-MM-DD'
        data_pagamento_str = data_pagamento.strftime('%Y-%m-%d')

        data = {
            "id_funcionario": id_funcionario_selecionado,
            "data_pagamento": data_pagamento_str,
            "provento_desconto": provento_desconto,
            "tipo": tipo,
            "valor": valor
        }

        result = supabase.table("folha_pagamento").insert(data).execute()

        if result.error:
            st.error(f"Erro ao inserir dados: {result.error.message}")
        else:
            st.success("Lançamento realizado com sucesso!")
