import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date

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

# --------------------------
# FORMULÁRIO DE DESPESAS
# --------------------------
with st.form("form_despesa"):
    filial = st.selectbox("Filial", filiais)
    funcionario = st.text_input("Funcionário")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    meio_pagamento = st.selectbox("Meio de Pagamento", meios_pagamento)
    recorrencia = st.selectbox("Recorrência", recorrencias)
    conta = st.selectbox("Conta", contas)

    # Escolher a data manualmente
    data_escolhida = st.date_input("Data da Despesa", date.today())

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

# --------------------------
# VISUALIZAÇÃO E EXCLUSÃO
# --------------------------
st.markdown("---")
st.header("Visualização de Despesas")

try:
    resposta = supabase.table("despesas").select("*").execute()
    df = resposta.data

    if df:
        import pandas as pd

        df = pd.DataFrame(df)
        df["data"] = pd.to_datetime(df["data"])

        st.subheader("Lista de Despesas")

        # Cabeçalho
        header_cols = st.columns([2,2,1,1,1,2,1])
        header_cols[0].write("**Código**")
        header_cols[1].write("**Data**")
        header_cols[2].write("**Filial**")
        header_cols[3].write("**Valor**")
        header_cols[4].write("**Pagamento**")
        header_cols[5].write("**Funcionário**")
        header_cols[6].write("**Ação**")

        # Linhas com botão apagar
        for index, row in df.sort_values("data", ascending=False).iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,1,1,1,2,1])

            col1.write(row['cod_pagamento'])
            col2.write(row["data"].date())
            col3.write(row["filial_id"])
            col4.write(f"R$ {row['valor']:.2f}")
            col5.write(row["meio_de_pagamento"])
            col6.write(row["funcionario"])

            if col7.button("Apagar", key=f"apagar_{row['cod_pagamento']}"):
                try:
                    supabase.table("despesas")\
                            .delete()\
                            .eq("cod_pagamento", row['cod_pagamento'])\
                            .execute()
                    st.success(f"Despesa {row['cod_pagamento']} apagada! Atualize a página.")
                except Exception as e:
                    st.error(f"Erro ao apagar: {e}")

    else:
        st.info("Nenhuma despesa registrada ainda.")

except Exception as e:
    st.error(f"Erro ao buscar despesas: {e}")
