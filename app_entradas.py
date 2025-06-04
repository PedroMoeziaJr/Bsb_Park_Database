import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Inicializa conexão com Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Caixa SCS")

# Lista de clientes
clientes_lista = [
    "Alex De Brito Bonifacio", "Alex Junio De Sousa Silva", "Atlantico Engenharia Ltda",
    "Bruna Ayres Cardoso", "Gabriel Ferreira Rego", "Guilherme Costa Macedo",
    "Joao Costa E Silva", "Jorge Luiz De Souza", "Jose Pereira De Araujo", "Rodrigo Merlo Nunes",
    "Leandro Ribeiro De Lima", "Milena Da Silva Santos Borges", "Tania Mara Meneses De Faria",
    "Vasco Azevedo", "Sergio Henrique Moreira Cunha", "Carolina Silva Lucena Dantas",
    "Neiane Andreato", "Luana Caixeta Paz", "Larissa Carolina Araujo Vieira",
    "Nannashara Cotrim Santana De Rez", "Antonio Ferreira Lima Filho",
    "Mariana Carvalho Pinheiro", "Isaet Gomes Da Silva Morais",
    "Marcello Novaes Fernandes Espind", "Cliente Rotativo Scs", "Bradesco Agencia 0606",
    "N&N Ass. E Cons Empresarial", "Bradesco S.A Dcps Varejo", "Bradesco Prime",
    "Bradesco Empresas", "Centro Auditivo Telex", "Top Tier", "Relações Institucionais",
    "Paulus Livraria", "Conselho Regional De Economia", "Ana Cristina Da Guarda Santana",
    "Keite Xavier De Oliveira", "Atlantico Engenharia Ltda", "Maira Cantieri Silveira Vieira",
    "Rafael Martins Aragao", "Samuel Correia Queiroz"
]

# Formulário
with st.form("form_entrada"):
    tipo_cliente = st.selectbox("Tipo de cliente", clientes_lista)
    forma_pagamento = st.selectbox("Forma de pagamento", ["dinheiro", "cartão", "Apurado", "pix"])
    valor_entrada = st.number_input("Valor da entrada (R$)", min_value=0.0, format="%.2f")
    qtd_entradas = st.number_input("Quantidade de entradas", min_value=1, step=1)
    submit_button = st.form_submit_button("Registrar entrada")

# Função para obter último ID
def get_last_id():
    response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
    if not response or not response.data:
        return 20845  # valor inicial
    return response.data[0]["id_entrada"]

# Registro da entrada
if submit_button:
    try:
        # Gera próximo ID
        ultimo_id = get_last_id()
        proximo_id = ultimo_id + 1

        # Busca código do cliente
        cliente_res = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", tipo_cliente).execute()
        if not cliente_res or not cliente_res.data:
            st.error("Código do cliente não encontrado.")
        else:
            cod_cliente = cliente_res.data[0]["cod_mensalista"]

            # Insere na tabela
            insert_response = supabase.table("entradas").insert({
                "id_entrada": proximo_id,
                "data_entrada": datetime.now().isoformat(),
                "tipo_cliente": tipo_cliente,
                "cod_cliente": cod_cliente,
                "forma_pagamento": forma_pagamento,
                "valor_entrada": valor_entrada,
                "qtd_entradas": qtd_entradas
            }).execute()

            if insert_response.data:
                st.success(f"Entrada registrada com sucesso! ID: {proximo_id}")
            else:
                st.error("Erro ao inserir no banco de dados.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao registrar a entrada: {e}")






st.subheader("Consultar entradas por cliente e data")

# Selecionar cliente e data
cliente_consulta = st.selectbox("Selecione o cliente", clientes_lista, key="consulta_cliente")
data_consulta = st.date_input("Selecione a data da entrada")

if st.button("Consultar entradas"):
    try:
        data_iso = datetime.combine(data_consulta, datetime.min.time()).isoformat()

        consulta = supabase.table("entradas")\
            .select("*")\
            .eq("tipo_cliente", cliente_consulta)\
            .gte("data_entrada", data_iso)\
            .lt("data_entrada", datetime.combine(data_consulta, datetime.max.time()).isoformat())\
            .order("data_entrada", desc=True)\
            .execute()

        if consulta.data:
            st.write(f"🔎 Entradas para **{cliente_consulta}** em **{data_consulta.strftime('%d/%m/%Y')}**:")
            st.dataframe(consulta.data)
        else:
            st.info("Nenhuma entrada encontrada para esse cliente nessa data.")

    except Exception as e:
        st.error(f"Erro na consulta: {e}")

