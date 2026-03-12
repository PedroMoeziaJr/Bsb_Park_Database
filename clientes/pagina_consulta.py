import streamlit as st
from clientes.crud_clientes import listar_filiais, listar_clientes_por_filial

def pagina_consulta():
    st.title("Consulta e Edição de Clientes")

    # Buscar filiais
    filiais = listar_filiais().data

    if not filiais:
        st.warning("Nenhuma filial encontrada no banco de dados.")
        return

    # Criar selectbox usando a coluna id_filial
    lista_filiais = [f["id_filial"] for f in filiais]

    filial_escolhida = st.selectbox(
        "Selecione a filial:",
        lista_filiais
    )

    # Buscar clientes da filial selecionada
    clientes = listar_clientes_por_filial(filial_escolhida).data

    if not clientes:
        st.info("Nenhum cliente encontrado para esta filial.")
        return

    st.dataframe(clientes)

    st.subheader("Buscar Cliente")
    cod = st.text_input("Código do Cliente para buscar")

    if st.button("Buscar"):
        cliente = buscar_cliente(cod).data
        if cliente:
            st.write("Cliente encontrado:")
            st.json(cliente)

            st.subheader("Editar Cliente")

            nome = st.text_input("Nome", cliente["nome_cliente"])
            id_filial = st.text_input("ID Filial", cliente["id_filial"])
            qntd = st.text_input("Qtd Entradas", cliente["qntd_entradas"])
            fundo = st.number_input("Fundo de Caixa", value=float(cliente["fundo_de_caixa"]))
            operador = st.text_input("Operador", cliente["operador"])
            forma = st.text_input("Forma de Pagamento", cliente["forma_de_pagamento"])
            boleto = st.text_input("Boleto", cliente["boleto"])
            tipo = st.text_input("Tipo de Cliente", cliente["tipo_de_cliente"])
            status = st.text_input("Status", cliente["status"])

            if st.button("Salvar Alterações"):
                atualizar_cliente(
                    cod,
                    {
                        "nome_cliente": nome,
                        "id_filial": id_filial,
                        "qntd_entradas": qntd,
                        "fundo_de_caixa": fundo,
                        "operador": operador,
                        "forma_de_pagamento": forma,
                        "boleto": boleto,
                        "tipo_de_cliente": tipo,
                        "status": status,
                    },
                )
                st.success("Cliente atualizado!")

            if st.button("Excluir Cliente"):
                deletar_cliente(cod)
                st.error("Cliente excluído!")
        else:

            st.warning("Cliente não encontrado.")

