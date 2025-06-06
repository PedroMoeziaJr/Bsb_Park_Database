import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Configurar Supabase
url = "https://seu-projeto.supabase.co"
key = "sua-chave-anonima"
supabase: Client = create_client(url, key)

# Lista limitada de clientes SCS
clientes_scs = [
    "Atlantico Engenharia Ltda",
    "Cliente Rotativo Scs",
    "Bradesco Agencia 0606",
    "N&N Ass. E Cons Empresarial",
    "Bradesco S.A Dcps Varejo",
    "Bradesco Prime",
    "Bradesco Empresas",
    "Centro Auditivo Telex",
    "Top Tier",
    "Relações Institucionais",
    "Paulus Livraria",
    "Conselho Regional De Economia",
    "Maira Cantieri Silveira Vieira"
]

st.title("Caixa SCS")

st.subheader("Registrar nova entrada")

with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Tipo de cliente", clientes_scs)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)

    data_entrada = st.date_input("Data da entrada", value=datetime.now().date())
    hora_entrada = st.time_input("Hora da entrada", value=datetime.now().time())

    submit_button = st.form_submit_button("Registrar entrada")

if submit_button:
    data_hora_entrada = datetime.combine(data_entrada, hora_entrada)

    # Inserir dados no Supabase
    entrada = {
        "tipo_cliente": tipo_cliente,
        "forma_pagamento": forma_pagamento,
        "valor": valor_entrada,
        "quantidade": qtd_entradas,
        "data_hora": data_hora_entrada.isoformat()
    }

    response = supabase.table("entradas").insert(entrada).execute()
    if response.status_code == 201:
        st.success("Entrada registrada com sucesso!")
    else:
        st.error(f"Erro ao registrar entrada: {response.data}")

st.subheader("Entradas registradas")

try:
    # Buscar somente entradas do tipo_cliente da lista SCS
    dados = supabase.table("entradas").select("*").in_("tipo_cliente", clientes_scs).order("data_hora", desc=True).execute()
    if dados.status_code != 200:
        st.error(f"Erro ao consultar entradas: {dados.data}")
    else:
        entradas = dados.data
        if entradas:
            for e in entradas:
                st.write(f"{e['data_hora']} | {e['tipo_cliente']} | R$ {e['valor']:.2f} | {e['forma_pagamento']} | Qtde: {e['quantidade']}")
                btn_key = f"del_{e['id']}"
                if st.button("Excluir entrada", key=btn_key):
                    del_resp = supabase.table("entradas").delete().eq("id", e["id"]).execute()
                    if del_resp.status_code == 204:
                        st.success("Entrada excluída com sucesso! Recarregue a página para atualizar.")
                    else:
                        st.error(f"Erro ao excluir entrada: {del_resp.data}")
        else:
            st.info("Nenhuma entrada encontrada.")
except Exception as err:
    st.error(f"Erro ao consultar entradas: {err}")

