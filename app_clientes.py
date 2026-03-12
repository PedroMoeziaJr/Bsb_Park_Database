import streamlit as st
from clientes.pagina_cadastro import pagina_cadastro
from clientes.pagina_consulta import pagina_consulta


def main():
    st.sidebar.title("Menu")
    opcao = st.sidebar.selectbox(
        "Selecione a página",
        ["Cadastro de Clientes", "Consulta de Clientes"]
    )

    if opcao == "Cadastro de Clientes":
        pagina_cadastro()
    elif opcao == "Consulta de Clientes":
        pagina_consulta()


if __name__ == "__main__":
    main()
