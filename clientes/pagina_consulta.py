import streamlit as st
from clientes.crud_clientes import (
    listar_clientes_por_filial,
    listar_filiais,
    buscar_cliente_por_nome,
    atualizar_cliente,
    deletar_cliente,
)


def pagina_consulta():

    if st.session_state.get("refresh_consulta"):
        st.session_state["refresh_consulta"] = False
        st.rerun()

    st.title("Consulta e Edição de Clientes")

    # Filiais
    filiais = listar_filiais().data
    lista_filiais = [f["id_filial"] for f in filiais]

    filial_escolhida = st.selectbox("Selecione a filial:", lista_filiais)

    st.subheader("Buscar cliente pelo nome")
    nome_busca = st.text_input("Digite parte do nome do cliente")

    # Busca
    if nome_busca.strip():
        clientes = buscar_cliente_por_nome(nome_busca).data
    else:
        clientes = listar_clientes_por_filial(filial_escolhida).data

    if not clientes:
        st.warning("Nenhum cliente encontrado.")
        return

    st.subheader("Resultados")
    st.dataframe(clientes, use_container_width=True)

    st.write("### Ações")

    for cliente in clientes:
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            st.write(f"{cliente['cod_cliente']} - {cliente['nome_cliente']}")

        with col2:
            if st.button("Editar", key=f"edit_{cliente['cod_cliente']}"):
                st.session_state["cliente_editando"] = cliente

        with col3:
            if st.button("Excluir", key=f"del_{cliente['cod_cliente']}"):
                deletar_cliente(cliente["cod_cliente"])
                st.success("Cliente excluído com sucesso!")
                st.session_state["refresh_consulta"] = True

    # Formulário de edição
    if "cliente_editando" in st.session_state:
        cliente = st.session_state["cliente_editando"]

        st.subheader(f"Editando cliente: {cliente['cod_cliente']}")

        novo_nome = st.text_input("Nome", cliente["nome_cliente"])

        formas_pagamento = ["Dinheiro", "Boleto", "Pix", "Transferência", "Cartão"]
        nova_forma = st.selectbox(
            "Forma de pagamento",
            formas_pagamento,
            index=formas_pagamento.index(cliente["forma_de_pagamento"])
        )

        tipos_cliente = ["Mensalista", "Tickets_Convenio", "Rotativo"]
        novo_tipo = st.selectbox(
            "Tipo de cliente",
            tipos_cliente,
            index=tipos_cliente.index(cliente["tipo_de_cliente"])
        )

        status_opcoes = ["Ativo", "Desativado"]
        novo_status = st.selectbox(
            "Status",
            status_opcoes,
            index=status_opcoes.index(cliente["status"])
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
            st.session_state["refresh_consulta"] = True
