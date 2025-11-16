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
# FORMULÁRIO DE DESPESAS (REGISTRO)
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

    # Data usada APENAS para registrar a despesa (dia é permitido aqui)
    data_registro = st.date_input("Data da Despesa (registro)", date.today())

    submitted = st.form_submit_button("Enviar")

    if submitted:
        # Obter último cod_pagamento
        try:
            dados = supabase.table("despesas")\
                .select("cod_pagamento")\
                .order("cod_pagamento", desc=True)\
                .limit(1)\
                .execute()
            ultimo_cod = dados.data[0]["cod_pagamento"] if dados.data else 100
        except Exception:
            ultimo_cod = 100

        novo_cod = ultimo_cod + 1

        nova_despesa = {
            "cod_pagamento": novo_cod,
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
# VISUALIZAÇÃO: buscar todos os registros primeiro
# --------------------------
st.header("Visualização de Despesas")

try:
    resposta = supabase.table("despesas").select("*").execute()
    registros = resposta.data if resposta.data else []
except Exception as e:
    st.error(f"Erro ao buscar despesas: {e}")
    registros = []

# Converte para DataFrame e prepara colunas de data
if registros:
    df_all = pd.DataFrame(registros)
    # tenta converter a coluna 'data' para datetime robustamente
    df_all["data"] = pd.to_datetime(df_all["data"], errors="coerce")
    # remove linhas com data inválida (se houver)
    df_all = df_all.dropna(subset=["data"]).copy()
    # tira timezone se houver
    try:
        df_all["data"] = df_all["data"].dt.tz_localize(None)
    except Exception:
        pass
else:
    df_all = pd.DataFrame(columns=[
        "cod_pagamento", "data", "filial_id", "funcionario",
        "valor", "meio_de_pagamento", "recorrencia", "conta"
    ])

# --------------------------
# Seletor de MÊS/ANO para FILTRAR (VISUALIZAÇÃO)
# --------------------------
col_filter_1, col_filter_2, col_filter_3 = st.columns([2,2,1])
with col_filter_1:
    # mês: mostra nomes para o usuário, mas guarda números internamente
    meses = [
        "01 - Janeiro","02 - Fevereiro","03 - Março","04 - Abril","05 - Maio","06 - Junho",
        "07 - Julho","08 - Agosto","09 - Setembro","10 - Outubro","11 - Novembro","12 - Dezembro"
    ]
    mes_idx = st.selectbox("Mês (filtrar)", options=list(range(1,13)), format_func=lambda x: meses[x-1], index=date.today().month-1)

with col_filter_2:
    # ano: se houver dados, usar anos existentes; senão, usar uma faixa em torno do ano atual
    if not df_all.empty:
        anos_disponiveis = sorted(df_all["data"].dt.year.unique().tolist(), reverse=True)
        ano_idx = st.selectbox("Ano (filtrar)", options=anos_disponiveis, index=0)
    else:
        ano_idx = st.selectbox("Ano (filtrar)", options=[date.today().year, date.today().year-1, date.today().year+1], index=0)

with col_filter_3:
    # botão para aplicar (opcional; filtro aplica automaticamente, mas deixo botão para controle)
    st.write("")  # filler
    if st.button("Atualizar visualização"):
        st.experimental_rerun()

# --------------------------
# Aplica filtro mês/ano
# --------------------------
mes_filtro = int(mes_idx)
ano_filtro = int(ano_idx)

df_filtrado = df_all[(df_all["data"].dt.month == mes_filtro) & (df_all["data"].dt.year == ano_filtro)].copy()

st.subheader(f"Despesas de {mes_filtro:02d}/{ano_filtro} — {len(df_filtrado)} registros")

# --------------------------
# Exibe tabela com botão apagar em cada linha
# --------------------------
if df_filtrado.empty:
    st.info("Nenhuma despesa encontrada neste mês/ano.")
else:
    # Cabeçalho
    header_cols = st.columns([1.2, 1.8, 1.6, 1.2, 1.4, 2.8, 1.0])
    header_cols[0].write("**Código**")
    header_cols[1].write("**Data**")
    header_cols[2].write("**Filial**")
    header_cols[3].write("**Valor**")
    header_cols[4].write("**Pagamento**")
    header_cols[5].write("**Funcionário**")
    header_cols[6].write("**Ação**")

    # Ordena por data decrescente e exibe
    for _, row in df_filtrado.sort_values("data", ascending=False).iterrows():
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2, 1.8, 1.6, 1.2, 1.4, 2.8, 1.0])

        col1.write(int(row["cod_pagamento"]))
        col2.write(row["data"].date().isoformat())
        col3.write(row.get("filial_id", ""))
        col4.write(f"R$ {float(row.get('valor', 0)):,.2f}")
        col5.write(row.get("meio_de_pagamento", ""))
        col6.write(row.get("funcionario", ""))

        # botão apagar na mesma linha — usa cod_pagamento como key
        key_btn = f"apagar_{int(row['cod_pagamento'])}"
        if col7.button("Apagar", key=key_btn):
            # confirmação simples (modal não existe nativo), usamos st.confirm-like via st.radio opcional
            if st.checkbox(f"Confirmar exclusão de {int(row['cod_pagamento'])}?", key=f"confirm_{key_btn}"):
                try:
                    supabase.table("despesas").delete().eq("cod_pagamento", int(row["cod_pagamento"])).execute()
                    st.success(f"Despesa {int(row['cod_pagamento'])} apagada.")
                    st.experimental_rerun()  # recarrega a página para atualizar lista
                except Exception as e:
                    st.error(f"Erro ao apagar: {e}")

# --------------------------
# Opcional: mostra resumo do mês (total)
# --------------------------
if not df_filtrado.empty:
    total_mes = df_filtrado["valor"].astype(float).sum()
    st.metric(label="Total do mês (R$)", value=f"R$ {total_mes:,.2f}")
