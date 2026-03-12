import streamlit as st
from clientes.crud_clientes import (
    listar_clientes_por_filial,
    listar_filiais,
    buscar_cliente_por_nome,
    atualizar_cliente
)

def pagina_consulta():
    st.title("Consulta e Edição de Clientes")

    # ============================
    # LISTAR FILIAIS
    # ============================
    filiais = listar_filiais().data
    lista_filiais = [f["id_filial"] for f in filiais]

    filial_escolhida = st.selectbox(
        "Selecione a filial:",
        lista_filiais
    )

    st.subheader("Buscar cliente pelo nome")
    nome_busca = st.text_input("Digite parte do nome do cliente")

    # ============================
    # BUSCA POR NOME
    # ============================
    if nome_busca.strip() != "":
        clientes = buscar_cliente_por_nome(nome_busca).data
    else:
        clientes = listar_clientes_por_filial(filial_escolhida).data

    if not clientes:
        st.warning("Nenhum cliente encontrado.")
        return

    st.subheader("Resultados")
    
    # ============================
    # LISTA COM BOTÃO DE EDITAR
    # ============================
    for cliente in clientes:
        with st.expander(f"{cliente['cod_cliente']} - {cliente['nome_cliente']}"):
            st.write("Filial:", cliente["id_filial"])
            st.write("Forma de pagamento:", cliente["forma_de_pagamento"])
            st.write("Tipo de cliente:", cliente["tipo_de_cliente"])
            st.write("Operador:", cliente["operador"])
            st.write("Status:", cliente["status"])

            if st.button(f"Editar {cliente['cod_cliente']}"):
                st.session_state["cliente_editando"] = cliente

    # ============================
    # FORMULÁRIO DE EDIÇÃO
    # ============================
    if "cliente_editando" in st.session_state:
        cliente = st.session_state["cliente_editando"]

        st.subheader(f"Editando cliente: {cliente['cod_cliente']}")

        novo_nome = st.text_input("Nome", cliente["nome_cliente"])
        nova_forma = st.selectbox(
            "Forma de pagamento",
            ["Dinheiro", "Boleto", "Pix", "Transferência", "Cartão"],
            index=["Dinheiro", "Boleto", "Pix", "Transferência", "Cartão"].index(cliente["forma_de_pagamento"])
        )
        novo_tipo = st.selectbox(
            "Tipo de cliente",
            ["Mensalista", "Tickets_Convenio", "Rotativo"],
            index=["Mensalista", "Tickets_Convenio", "Rotativo"].index(cliente["tipo_de_cliente"])
        )
        novo_status = st.selectbox(
            "Status",
            ["Ativo", "Inativo"],
            index=0 if cliente["status"] == "Ativo" else 1
        )

        if st.button("Salvar alterações"):
            dados_atualizados = {
                "nome_cliente": novo_nome,
                "forma_de_pagamento": nova_forma,
                "tipo_de_cliente": novo_tipo,
                "status": novo_status
            }

            atualizar_cliente(cliente["cod_cliente"], dados_atualizados)
            st.success("Cliente atualizado com sucesso!")
            del st.session_state["cliente_editando"]
            st.experimental_rerun()
