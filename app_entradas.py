import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Inicializa conexão com Supabase usando st.secrets corretamente
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

# Título do app
st.title("Caixa SCS")

# Lista de clientes
clientes = [
    "Alex De Brito Bonifacio", "Alex Junio De Sousa Silva", "Atlantico Engenharia Ltda",
    "Bruna Ayres Cardoso", "Gabriel Ferreira Rego", "Guilherme Costa Macedo",
    "Joao Costa E Silva", "Jorge Luiz De Souza", "Jose Pereira De Araujo",
    "Rodrigo Merlo Nunes", "Leandro Ribeiro De Lima", "Milena Da Silva Santos Borges",
    "Tania Mara Meneses De Faria", "Vasco Azevedo", "Sergio Henrique Moreira Cunha",
    "Carolina Silva Lucena Dantas", "Neiane Andreato", "Luana Caixeta Paz",
    "Larissa Carolina Araujo Vieira", "Nannashara Cotrim Santana De Rez",
    "Antonio Ferreira Lima Filho", "Mariana Carvalho Pinheiro", "Isaet Gomes Da Silva Morais",
    "Marcello Novaes Fernandes Espind", "Cliente Rotativo Scs", "Bradesco Agencia 0606",
    "N&N Ass. E Cons Empresarial", "Bradesco S.A Dcps Varejo", "Bradesco Prime",
    "Bradesco Empresas", "Centro Auditivo Telex", "Top Tier",
    "Relações Institucionais", "Paulus Livraria", "Conselho Regional De Economia",
    "Ana Cristina Da Guarda Santana", "Keite Xavier De Oliveira", "Atlantico Engenharia Ltda",
    "Maira Cantieri Silveira Vieira", "Rafael Martins Aragao", "Samuel Correia Queiroz"
]

# Lista de formas de pagamento
formas_pagamento = ["dinheiro", "cartão", "Apurado", "pix"]

# Campos do formulário
with st.form("entrada_form"):
    tipo_cliente = st.selectbox("Tipo de Cliente", clientes)
    forma_pagamento = st.selectbox("Forma de Pagamento", formas_pagamento)
    valor_entrada = st.number_input("Valor da Entrada", step=0.01, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de Entradas", step=1, min_value=1)

    submitted = st.form_submit_button("Registrar Entrada")

if submitted:
    try:
        # Recupera o próximo ID
        registros = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
        ultimo_id = registros.data[0]["id_entrada"] if registros.data else 20844
        novo_id = ultimo_id + 1

        # Recupera o código do cliente da tabela 'clientes'
        cliente_resultado = supabase.table("clientes").select("cod_cliente").eq("nome", tipo_cliente).execute()

        if not cliente_resultado.data:
            st.error("Cliente não encontrado na tabela 'clientes'. Verifique o nome.")
        else:
            cod_cliente = cliente_resultado.data[0]["cod_cliente"]

            nova_entrada = {
                "id_entrada": novo_id,
                "data_entrada": datetime.now().strftime("%Y-%m-%d"),
                "tipo_de_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": float(valor_entrada),
                "qtd_entradas": int(qtd_entradas)
            }

            resultado = supabase.table("entradas").insert(nova_entrada).execute()
            st.success(f"Entrada registrada com sucesso! ID: {novo_id}")

    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")
