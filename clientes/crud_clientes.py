from supabase import create_client, Client
import os

# ============================
# CONFIGURAÇÃO DO SUPABASE
# ============================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nome da tabela de clientes
TABELA = "clientes"


# ============================
# LISTAR FILIAIS
# ============================

def listar_filiais():
    """
    Retorna todas as filiais cadastradas.
    A tabela 'filiais' deve ter a coluna 'id_filial'.
    """
    return supabase.table("filiais").select("*").execute()


# ============================
# LISTAR CLIENTES
# ============================

def listar_clientes():
    """
    Retorna todos os clientes sem filtro.
    """
    return supabase.table(TABELA).select("*").execute()


def listar_clientes_por_filial(id_filial):
    """
    Retorna clientes filtrados pela filial.
    A coluna correta na tabela clientes é 'id_filial'.
    """
    return supabase.table(TABELA).select("*").eq("id_filial", id_filial).execute()


# ============================
# CRIAR CLIENTE
# ============================

def criar_cliente(dados):
    """
    Insere um novo cliente no banco.
    'dados' deve ser um dicionário contendo:
    nome, telefone, id_filial, forma_pagamento,
    tipo_cliente, qntd_entradas, operador
    """
    return supabase.table(TABELA).insert(dados).execute()


# ============================
# ATUALIZAR CLIENTE
# ============================

def atualizar_cliente(id_cliente, novos_dados):
    """
    Atualiza os dados de um cliente específico.
    """
    return supabase.table(TABELA).update(novos_dados).eq("id", id_cliente).execute()


# ============================
# DELETAR CLIENTE
# ============================

def deletar_cliente(id_cliente):
    """
    Remove um cliente pelo ID.
    """
    return supabase.table(TABELA).delete().eq("id", id_cliente).execute()
