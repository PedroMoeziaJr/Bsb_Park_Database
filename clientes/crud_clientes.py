from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABELA = "clientes"

# ============================
# LISTAR FILIAIS
# ============================

def listar_filiais():
    return supabase.table("filiais").select("*").execute()

# ============================
# LISTAR CLIENTES
# ============================

def listar_clientes():
    return supabase.table(TABELA).select("*").execute()

def listar_clientes_por_filial(id_filial):
    return supabase.table(TABELA).select("*").eq("id_filial", id_filial).execute()

# ============================
# CRIAR CLIENTE
# ============================

def criar_cliente(dados):
    return supabase.table(TABELA).insert(dados).execute()

# ============================
# ATUALIZAR CLIENTE
# ============================

def atualizar_cliente(id_cliente, novos_dados):
    return supabase.table(TABELA).update(novos_dados).eq("cod_cliente", id_cliente).execute()

# ============================
# DELETAR CLIENTE
# ============================

def deletar_cliente(id_cliente):
    return supabase.table(TABELA).delete().eq("cod_cliente", id_cliente).execute()

def buscar_cliente_por_nome(nome):
    return (
        supabase.table("clientes")
        .select("*")
        .ilike("nome_cliente", f"%{nome}%")
        .execute()
    )

