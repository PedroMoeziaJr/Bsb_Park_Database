import streamlit as st
from clientes.crud_clientes import criar_cliente, listar_filiais

def pagina_cadastro():
    st.title("Cadastro de Clientes")

    # ============================
    # FILIAIS
    # ============================
    filiais = listar_filiais().data
    lista_filiais = [f["id_filial"] for f in filiais]

    filial_escolhida = st.selectbox(
        "Selecione a filial:",
        lista_filiais
    )

    # ============================
    # FORMA DE PAGAMENTO
    # ============================
    formas_pagamento = ["Dinheiro", "Boleto", "Pix", "Transferência", "Cartão"]

    forma_pagamento = st.selectbox(
        "Forma de pagamento:",
        formas_pagamento
    )

    # ============================
    # TIPO DE CLIENTE
    # ============================
    tipos_cliente = ["Mensalista", "Tickets_Convenio", "Rotativo"]

    tipo_cliente = st.selectbox(
        "Tipo de cliente:",
        tipos_cliente
    )

    # ============================
    # CAMPOS AUTOMÁTICOS
    # ============================
    qntd_entradas = "a verificar"
    operador = "Sem Operador"

    # ============================
    # CAMPOS DE TEXTO
    # ============================
    cod_cliente = st.text_input("Código do Cliente")
    nome_cliente = st.text_input("Nome do Cliente")

    # ============================
    # BOTÃO DE CADASTRO
    # ============================
    if st.button("Cadastrar Cliente"):
    dados = {
        "cod_cliente": cod_cliente,
        "nome_cliente": nome_cliente,
        "id_filial": filial_escolhida
    }

    st.write("DEBUG:", dados)

    criar_cliente(dados)
    st.success("Cliente cadastrado com sucesso!")
