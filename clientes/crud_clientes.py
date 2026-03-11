from supabase import create_client
import os

# Conexão com Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABELA = "clientes"

# -----------------------------
# CREATE
# -----------------------------
def criar_cliente(dados: dict):
    return supabase.table(TABELA).insert(dados).execute()


# -----------------------------
# READ
# -----------------------------
def listar_clientes():
    return supabase.table(TABELA).select("*").execute()


def buscar_cliente(cod_cliente: str):
    return supabase.table(TABELA).select("*").eq("cod_cliente", cod_cliente).single().execute()


# -----------------------------
# UPDATE
# -----------------------------
def atualizar_cliente(cod_cliente: str, dados: dict):
    return (
        supabase.table(TABELA)
        .update(dados)
        .eq("cod_cliente", cod_cliente)
        .execute()
    )


# -----------------------------
# DELETE
# -----------------------------
def deletar_cliente(cod_cliente: str):
    return (
        supabase.table(TABELA)
        .delete()
        .eq("cod_cliente", cod_cliente)
        .execute()
    )