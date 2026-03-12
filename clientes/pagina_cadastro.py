import streamlit as st
from clientes.crud_clientes import criar_cliente, listar_filiais


def pagina_cadastro():

    # Refresh seguro
    if st.session_state.get("refresh_cadastro"):
        st.session_state["refresh_cadastro"] = False
        st.rerun()

    st.title("Cadastro de Clientes")

    # Filiais
    filiais = listar_filiais().data
    lista_filiais = [f["id_filial"] for f in filiais]

    filial_escolhida = st.selectbox("Selecione a filial:", lista_filiais)

    # Forma de pagamento
    formas_pagamento = ["Dinheiro", "Boleto", "Pix", "Transferência", "Cartão"]
    forma_pagamento = st.selectbox("Forma de pagamento:", formas_pagamento)

    # Tipo de cliente
    tipos_cliente = ["Mensalista", "Tickets_Convenio", "Rotativo"]
    tipo_cliente = st.selectbox("Tipo de cliente:", tipos_cliente)

    # Campos automáticos
    qntd_entradas = "a verificar"
    operador = "Sem Operador"

    # Campos de texto
    cod_cliente = st.text_input("Código do Cliente")
    nome_cliente = st.text_input("Nome do Cliente")

    if st.button("Cadastrar Cliente"):

        if not cod_cliente or not nome_cliente:
            st.error("Preencha o código e o nome do cliente.")
            return

        dados = {
            "cod_cliente": cod_cliente,
            "nome_cliente": nome_cliente,
            "id_filial": filial_escolhida,
            "forma_de_pagamento": forma_pagamento,
            "tipo_de_cliente": tipo_cliente,
            "qntd_entradas": qntd_entradas,
            "operador": operador,
            "status": "Ativo",
            "boleto": "",
            "fundo_de_caixa": 0
        }

        criar_cliente(dados)
        st.success("Cliente cadastrado com sucesso!")

        st.session_state["refresh_cadastro"] = True
        st.rerun()
