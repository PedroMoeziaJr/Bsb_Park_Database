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

# Último id_entrada para gerar o próximo automaticamente
dados = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
ultimo_id = dados.data[0]["id_entrada"] if dados.data else 20845  # caso não tenha nenhum, começa do 20845

id_entrada = ultimo_id + 1
data_entrada = date.today()

# Lista de clientes
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

# Exibe o formulário
st.write(f"**ID da Entrada:** {id_entrada}")
st.write(f"**Data da Entrada:** {data_entrada}")

tipo_cliente = st.selectbox("Tipo de Cliente", clientes)
forma_pagamento = st.selectbox("Forma de Pagamento", formas_pagamento)
valor_entrada = st.number_input("Valor da Entrada", min_value=0.0, format="%.2f")
qtd_entradas = st.number_input("Quantidade de Entradas", min_value=1, step=1)

if st.button("Registrar Entrada"):
    # Busca cod_mensalista do cliente selecionado
    cliente_info = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", tipo_cliente).execute()

    if cliente_info.data and len(cliente_info.data) > 0:
        cod_cliente = cliente_info.data[0]["cod_mensalista"]
    else:
        st.error("Cliente não encontrado na tabela clientes.")
        st.stop()

    nova_entrada = {
        "id_entrada": id_entrada,
        "data_entrada": str(data_entrada),  # formato date como string ISO
        "cod_cliente": cod_cliente,
        "tipo_cliente": tipo_cliente,
        "forma_pagamento": forma_pagamento,
        "valor_entrada": valor_entrada,
        "qtd_entradas": int(qtd_entradas)
    }

    try:
        resultado = supabase.table("entradas").insert(nova_entrada).execute()
        if resultado.status_code == 201:
            st.success("Entrada registrada com sucesso!")
        else:
            st.error(f"Erro ao registrar a entrada: {resultado.data}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")
