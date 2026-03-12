from supabase import create_client, Client

# Ajuste essas variáveis com os dados do seu projeto
SUPABASE_URL = "https://clxuxrlqbkdadhkpzaly.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNseHV4cmxxYmtkYWRoa3B6YWx5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg5Nzg3NjgsImV4cCI6MjA2NDU1NDc2OH0.aMgo3gBA9Rb_H-Oex2nQ8SccmSfMNKv8TwyAixan2Wk"  # NÃO USE publishable

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABELA_CLIENTES = "clientes"
TABELA_FILIAIS = "filiais"


def listar_filiais():
    return supabase.table(TABELA_FILIAIS).select("*").execute()


def listar_clientes_por_filial(id_filial: str):
    return (
        supabase.table(TABELA_CLIENTES)
        .select("*")
        .eq("id_filial", id_filial)
        .order("cod_cliente")
        .execute()
    )


def criar_cliente(dados: dict):
    return supabase.table(TABELA_CLIENTES).insert(dados).execute()


def buscar_cliente_por_nome(nome: str):
    return (
        supabase.table(TABELA_CLIENTES)
        .select("*")
        .ilike("nome_cliente", f"%{nome}%")
        .order("cod_cliente")
        .execute()
    )


def atualizar_cliente(cod_cliente: str, dados: dict):
    return (
        supabase.table(TABELA_CLIENTES)
        .update(dados)
        .eq("cod_cliente", cod_cliente)
        .execute()
    )


def deletar_cliente(cod_cliente: str):
    return (
        supabase.table(TABELA_CLIENTES)
        .delete()
        .eq("cod_cliente", cod_cliente)
        .execute()
    )


