import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Inicializa a conexão com o Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

st.title("Controle de Entradas - BSB Park")
st.subheader("Registrar Entrada")

nome_cliente = st.text_input("Nome do Cliente")
placa = st.text_input("Placa do Veículo")
caixa = st.selectbox("Caixa:", ["Caixa SCS", "Caixa Garagem"])

if st.button("Registrar Entrada"):
    if nome_cliente and placa:
        try:
            # Busca o cod_mensalista
            result = supabase.table("clientes").select("cod_mensalista").eq("nome_cliente", nome_cliente).execute()
            cod_cliente = result.data[0]["cod_mensalista"] if result.data else None

            if not cod_cliente:
                st.error("Cliente não encontrado.")
            else:
                id_entrada = get_last_id() + 1
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                insert_response = supabase.table("entradas").insert({
                    "id_entrada": id_entrada,
                    "cod_cliente": cod_cliente,
                    "placa": placa,
                    "data_hora_entrada": data_hora,
                    "caixa": caixa
                }).execute()

                # Checa sucesso
                if hasattr(insert_response, 'data') and insert_response.data:
                    st.success("Entrada registrada com sucesso!")
                else:
                    st.error(f"Erro ao registrar entrada: {insert_response}")

        except Exception as e:
            st.error(f"Ocorreu um erro ao registrar a entrada: {e}")
    else:
        st.warning("Preencha todos os campos para registrar a entrada.")

def get_last_id():
    try:
        response = supabase.table("entradas").select("id_entrada").order("id_entrada", desc=True).limit(1).execute()
        data = getattr(response, 'data', None)
        if not data:
            return 20845
        return data[0]["id_entrada"]
    except Exception:
        return 20845

