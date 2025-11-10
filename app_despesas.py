import streamlit as st
from datetime import datetime
from supabase import create_client, Client
from dateutil.parser import isoparse

st.set_page_config(page_title="Despesas", page_icon="💸", layout="centered")
st.title("Cadastro e Gestão de Despesas")

# --- Conexão com Supabase (direto no código, sem secrets) ---
# ⚠️ Substitua pelos valores reais do seu projeto Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- Helpers ---
def get_next_cod_pagamento():
    res = supabase.table("despesas").select("cod_pagamento").order("cod_pagamento", desc=True).limit(1).execute()
    if res.data:
        return int(res.data[0]["cod_pagamento"]) + 1
    return 1

def get_filiais():
    res = supabase.table("filiais").select("id_filial").execute()
    return [row["id_filial"] for row in res.data] if res.data else []

def inserir_despesa(payload: dict):
    return supabase.table("despesas").insert(payload).execute()

def listar_despesas_mes_vigente():
    hoje = datetime.today()
    res = supabase.table("despesas").select("*").execute()
    dados = res.data or []
    filtrados = []
    for d in dados:
        try:
            dt = isoparse(d["data"])
        except Exception:
            dt = datetime.fromisoformat(d["data"])
        if dt.month == hoje.month and dt.year == hoje.year:
            filtrados.append(d)
    return filtrados

def apagar_por_cod_pagamento(cod: int):
    return supabase.table("despesas").delete().eq("cod_pagamento", cod).execute()

# --- Formulário ---
st.subheader("Nova despesa")

filiais = get_filiais()
with st.form("form_despesas"):
    cod_pagamento = get_next_cod_pagamento()
    st.text_input("Código do Pagamento (auto)", value=str(cod_pagamento), disabled=True)

    data = st.date_input("Data da despesa", value=datetime.today())
    filial_id = st.selectbox("Filial (id_filial)", filiais) if filiais else st.text_input("Filial (id_filial)")
    funcionario = st.text_input("Nome da despesa")
    valor = st.number_input("Valor da despesa", step=0.01, format="%.2f", min_value=0.0)
    meio_pagamento = st.selectbox("Meio de pagamento", ["dinheiro", "cartão", "pix", "transferencia", "boleto"])
    recorrencia = st.selectbox("Recorrência", ["fixa", "variável"])
    conta = st.selectbox(
        "Conta",
        [
            "bancária", "condomínio", "contábil_jurídico", "energia",
            "internet_telefone", "operacional", "pessoal", "recursos humanos",
            "salário", "tributo", "vale refeição", "vale transporte"
        ]
    )

    submitted = st.form_submit_button("Salvar")
    if submitted:
        if not funcionario:
            st.error("Informe o nome da despesa.")
        else:
            payload = {
                "cod_pagamento": cod_pagamento,
                "data": str(data),  # 'YYYY-MM-DD'
                "filial_id": filial_id,
                "funcionário": funcionario,   # ⚠️ Confirme se sua tabela usa acento
                "valor": float(valor),
                "meio de pagamento": meio_pagamento,  # ⚠️ Confirme se sua tabela usa espaço
                "recorrencia": recorrencia,
                "conta": conta
            }
            try:
                inserir_despesa(payload)
                st.success(f"Despesa {cod_pagamento} cadastrada com sucesso!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- Listagem do mês vigente ---
st.subheader("Despesas do mês vigente")
despesas_mes = listar_despesas_mes_vigente()
if despesas_mes:
    st.dataframe(despesas_mes, use_container_width=True)
    ids_despesas = [d["cod_pagamento"] for d in despesas_mes if "cod_pagamento" in d]
    escolha = st.selectbox("Selecione o código da despesa para apagar", ids_despesas)
    if st.button("Apagar despesa selecionada"):
        try:
            apagar_por_cod_pagamento(escolha)
            st.success(f"Despesa {escolha} apagada com sucesso!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Erro ao apagar: {e}")
else:
    st.info("Nenhuma despesa cadastrada neste mês.")
