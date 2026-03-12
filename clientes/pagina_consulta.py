import streamlit as st
from clientes.crud_clientes import listar_clientes_por_filial, listar_filiais, buscar_cliente_por_nome

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
        resultado = buscar_cliente_por_nome(nome_busca).data

        if resultado:
            st.success(f"{len(resultado)} cliente(s) encontrado(s)")
            st.table(resultado)
        else:
            st.warning("Nenhum cliente encontrado com esse nome.")
        return  # Evita mostrar a lista completa abaixo

    # ============================
    # LISTAR CLIENTES DA FILIAL
    # ============================
    st.subheader(f"Clientes da filial {filial_escolhida}")

    clientes = listar_clientes_por_filial(filial_escolhida).data

    if clientes:
        st.table(clientes)
    else:
        st.info("Nenhum cliente cadastrado nessa filial.")

