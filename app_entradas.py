import streamlit as st
from supabase import create_client, Client

# Inicializa conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Lista de clientes usada no app
clientes_lista = [
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

st.title("🔍 Verificador de clientes no Supabase")

# Consulta todos os nomes da tabela clientes
res = supabase.table("clientes").select("cod_cliente, nome_cliente").execute()

if not res or not res.data:
    st.error("Não foi possível recuperar os clientes do Supabase.")
else:
    nomes_supabase = [c["nome_cliente"] for c in res.data]

    encontrados = []
    similares = []
    nao_encontrados = []

    for nome in clientes_lista:
        if nome in nomes_supabase:
            encontrados.append(nome)
        else:
            # Verifica se há nomes parecidos
            parecidos = [n for n in nomes_supabase if nome.lower() in n.lower()]
            if parecidos:
                similares.append((nome, parecidos))
            else:
                nao_encontrados.append(nome)

    st.subheader("✅ Nomes encontrados exatamente:")
    for nome in encontrados:
        st.markdown(f"- {nome}")

    st.subheader("🧐 Nomes com correspondência parcial:")
    for nome, lista in similares:
        st.markdown(f"- **{nome}** → Possíveis correspondências: {', '.join(lista)}")

    st.subheader("❌ Nomes não encontrados:")
    for nome in nao_encontrados:
        st.markdown(f"- {nome}")
