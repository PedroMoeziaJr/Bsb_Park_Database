import streamlit as st
from clientes.pagina_cadastro import pagina_cadastro
from clientes.pagina_consulta import pagina_consulta

menu = st.sidebar.selectbox(
    "Menu",
    ["Cadastro de Clientes", "Consulta de Clientes"]
)

if menu == "Cadastro de Clientes":
    pagina_cadastro()

elif menu == "Consulta de Clientes":
    pagina_consulta()
