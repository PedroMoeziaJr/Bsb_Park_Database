import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Substitua com os seus dados reais
SUPABASE_URL = "https://clxuxrlqbkdadhkpzaly.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"

# Inicializa o cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Formulário de Despesas")

# Campos do formulário
filial = st.selectbox("Filial", [
    "01_SCS", "02_Taguatinga", "03_Ed_Prime", "04_504", "05_Rio_de_Janeiro",
    "06_Imperatriz_MA", "07_Itumbiara_GO", "08_Ituiutaba_MG", "09_Matriz",
    "10_PF_Ped_", "11_PF_CEL_"
])
funcionario = st.text_input("Nome do Funcionário")
valor = st.text_input("Valor (use ponto como separador decimal)", placeholder="Ex: 120.50")
meio_pagamento = st.selectbox("Meio de Pagamento", ["Pix", "Internet", "Dda", "Boleto", "Transferencia"])
recorrencia = st.selectbox("Recorrência", ["Extra", "Fixa"])

if st.button("Enviar"):
    try:
        # Recupera último cod_pagamento
        dados = supabase.table("despesas").select("cod_pagamento").order("cod_pagamento", desc=True).limit(1).execute()
        if dados.data:
            ultimo_cod = dados.data[0]["cod_pagamento"]
        else:
            ultimo_cod = 100  # valor inicial se não houver registros
        
        novo_cod = ultimo_cod + 1
        data_hoje = datetime.now().strftime("%Y-%m-%d")

        # Cria dicionário com os dados no formato correto
        nova_despesa = {
            "cod_pagamento": novo_cod,
            "data": data_hoje,
            "filial_id": filial,
            "funcionario": funcionario,
            "valor": float(valor),
            "meio_de_pagamento": meio_pagamento,
            "recorrencia": recorrencia
        }

        # Insere no Supabase
        resultado = supabase.table("despesas").insert(nova_despesa).execute()

        st.success(f"Despesa registrada com sucesso! Código: {novo_cod}")

    except Exception as e:
        st.error(f"Erro ao registrar despesa: {e}")
