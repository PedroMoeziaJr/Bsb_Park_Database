import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date, time

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("📥 Caixa - SCS")

# --- LISTA RESTRITA DE CLIENTES ---
clientes_filtrados = [
    "Atlantico Engenharia Ltda", "Cliente Rotativo Scs", "Bradesco Agencia 0606",
    "N&N Ass. E Cons Empresarial", "Bradesco S.A Dcps Varejo", "Bradesco Prime",
    "Bradesco Empresas", "Centro Auditivo Telex", "Top Tier", "Relações Institucionais",
    "Paulus Livraria", "Conselho Regional De Economia", "Maira Cantieri Silveira Vieira"
]

# --- FORMULÁRIO DE NOVA ENTRADA ---
st.subheader("📝 Registrar nova entrada")

with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Cliente", clientes_filtrados)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)

    # Campo para data e hora manuais
    data_manual = st.date_input("Data da entrada", value=datetime.now().date())
    hora_manual = st.time_input("Hora da entrada", value=datetime.now().time())

    submit = st.form_submit_button("💾 Registrar entrada")

# --- FUNÇÃO PARA PRÓXIMO ID ---
def get_next_id():
    res = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    return (res.data[0]["id_entrada"] + 1) if res.data else 20845

# --- INSERIR ENTRADA ---
if submit:
    try:
        cliente_info = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", tipo_cliente).execute()
        if not cliente_info.data:
            st.error("Cliente não encontrado no banco de dados.")
        else:
            cod_cliente = cliente_info.data[0]["cod_mensalista"]
            novo_id = get_next_id()

            data_hora_completa = datetime.combine(data_manual, hora_manual).isoformat()

            entrada = {
                "id_entrada": novo_id,
                "data_entrada": data_hora_completa,
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas
            }

            resp = supabase.table("entradas").insert(entrada).execute()

            if resp.data:
                st.success(f"✅ Entrada registrada com sucesso! ID: {novo_id}")
            else:
                st.error("❌ Erro ao salvar no banco de dados.")
    except Exception as e:
        st.error(f"Erro ao registrar entrada: {e}")

# --- CONSULTA E EXCLUSÃO DE ENTRADAS ---
st.subheader("📆 Consultar e excluir entradas")

data_consulta = st.date_input("Selecione a data para consulta", key="consulta_data", value=datetime.now().date())
inicio = datetime.combine(data_consulta, time.min).isoformat()
fim = datetime.combine(data_consulta, time.max).isoformat()

try:
    resultado = supabase.table("entradas") \
        .select("id_entrada, tipo_cliente, valor_entrada, forma_pagamento, qtd_entradas, data_entrada") \
        .gte("data_entrada", inicio) \
        .lte("data_entrada", fim) \
        .order("data_entrada", desc=True) \
        .execute()

    if resultado.data:
        total = 0.0
        for row in resultado.data:
            id_entrada = row["id_entrada"]
            cliente = row["tipo_cliente"]
            valor = row["valor_entrada"]
            forma = row["forma_pagamento"]
            qtd = row["qtd_entradas"]
            hora = datetime.fromisoformat(row["data_entrada"]).strftime("%H:%M:%S")

            st.markdown(f"**ID {id_entrada}** | {cliente} | 💰 R$ {valor:.2f} | {forma} | Qtd: {qtd} | 🕒 {hora}")
            col1, col2 = st.columns([8, 2])
            with col2:
                if st.button(f"❌ Excluir {id_entrada}", key=f"del_{id_entrada}"):
                    try:
                        supabase.table("entradas").delete().eq("id_entrada", id_entrada).execute()
                        st.success(f"Entrada ID {id_entrada} excluída com sucesso.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir entrada: {e}")

            total += valor
        st.success(f"💰 Total do dia: R$ {total:.2f}")
    else:
        st.info("Nenhuma entrada registrada para este dia.")

except Exception as e:
    st.error(f"Erro ao consultar entradas: {e}")

