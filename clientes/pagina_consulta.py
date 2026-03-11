import streamlit as st
from clientes.crud_clientes import listar_clientes, buscar_cliente, atualizar_cliente, deletar_cliente

def pagina_consulta():
    st.title("Consulta e Edição de Clientes")

    clientes = listar_clientes().data

    if not clientes:
        st.info("Nenhum cliente cadastrado.")
        return

    st.subheader("Lista de Clientes")
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