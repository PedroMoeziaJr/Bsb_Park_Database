import streamlit as st
from supabase import create_client, Client
from datetime import date

# Função para inicializar conexão com Supabase
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.title("Caixa SCS")

# Lista de clientes para dropdown
clientes = [
    "Alex De Brito Bonifacio",
    "Alex Junio De Sousa Silva",
    "Atlantico Engenharia Ltda",
    "Bruna Ayres Cardoso",
    "Gabriel Ferreira Rego",
    "Guilherme Costa Macedo",
    "Joao Costa E Silva",
    "Jorge Luiz De Souza",
    "Jose Pereira De Araujo",
    "Rodrigo Merlo Nunes",
    "Leandro Ribeiro De Lima",
    "Milena Da Silva Santos Borges",
    "Tania Mara Meneses De Faria",
    "Vasco Azevedo",
    "Sergio Henrique Moreira Cunha",
    "Carolina Silva Lucena Dantas",
    "Neiane Andreato",
    "Luana Caixeta Paz",
    "Larissa Carolina Araujo Vieira",
    "Nannashara Cotrim Santana De Rez",
    "Antonio Ferreira Lima Filho",
    "Mariana Carvalho Pinheiro",
    "Isaet Gomes Da Silva Morais",
    "Marcello Novaes Fernandes Espind",
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
    "Ana Cristina Da Guarda Santana",
    "Keite Xavier De Oliveira",
    "Atlantico Engenharia Ltda",
    "Maira Cantieri Silveira Vieira",
    "Rafael Martins Aragao",
    "Samuel Correia Queiroz"
]

# Lista de formas de pagamento
formas_pagamento = ['dinheiro', 'cartão', 'Apurado', 'pix']

# Obter o último id_entrada para gerar próximo
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if response.error or not response.data:
        return 20845  # valor padrão se falhar na consulta
    return response.data[0]["id_entrada"]

ultimo_id = get_last_id()
novo_id = ultimo_id + 1

# Seleção de cliente no dropdown
cliente_selecionado = st.selectbox("Tipo de cliente", clientes)

# Obter cod_mensalista do cliente selecionado
def get_cod_cliente(nome_cliente):
    response = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", nome_cliente).execute()
    if response.error or not response.data:
        return None
    return response.data[0]["cod_mensalista"]

cod_cliente = get_cod_cliente(cliente_selecionado)

forma_pagamento_selecionada = st.selectbox("Forma de pagamento", formas_pagamento)

valor_entrada = st.number_input("Valor da entrada", min_value=0.0, format="%.2f")

qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)

if st.button("Registrar entrada"):
    nova_entrada = {
        "id_entrada": novo_id,
        "data_entrada": str(date.today()),
        "tipo_cliente": cliente_selecionado,
        "cod_cliente": cod_cliente,
        "forma_pagamento": forma_pagamento_selecionada,
        "valor_entrada": valor_entrada,
        "qtd_entradas": qtd_entradas,
    }
    try:
        resultado = supabase.table("entradas").insert(nova_entrada).execute()
        if resultado.error is None:
            st.success("Entrada registrada com sucesso!")
        else:
            st.error(f"Erro ao registrar a entrada: {resultado.error.message}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")

