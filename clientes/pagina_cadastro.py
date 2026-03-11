import streamlit as st
from clientes.crud_clientes import criar_cliente

def pagina_cadastro():
    st.title("Cadastro de Clientes")

    cod_cliente = st.text_input("Código do Cliente")
    nome_cliente = st.text_input("Nome do Cliente")
    id_filial = st.text_input("ID da Filial")
    qntd_entradas = st.text_input("Quantidade de Entradas")
    fundo_de_caixa = st.number_input("Fundo de Caixa", step=0.01)
    operador = st.text_input("Operador")
    forma_de_pagamento = st.text_input("Forma de Pagamento")
    boleto = st.text_input("Boleto")
    tipo_de_cliente = st.text_input("Tipo de Cliente")
    status = st.text_input("Status")

    if st.button("Cadastrar Cliente"):
        dados = {
            "cod_cliente": cod_cliente,
            "nome_cliente": nome_cliente,
            "id_filial": id_filial,
            "qntd_entradas": qntd_entradas,
            "fundo_de_caixa": fundo_de_caixa,
            "operador": operador,
            "forma_de_pagamento": forma_de_pagamento,
            "boleto": boleto,
            "tipo_de_cliente": tipo_de_cliente,
            "status": status,
        }

        criar_cliente(dados)
        st.success("Cliente cadastrado com sucesso!")