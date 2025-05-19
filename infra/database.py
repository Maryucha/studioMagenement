# infra/database.py
"""
Módulo de infraestrutura responsável pela conexão com o banco PostgreSQL (via Neon)
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_connection():
    """
    Retorna uma nova conexão com o banco de dados PostgreSQL (Neon via st.secrets).

    Returns:
        psycopg2.extensions.connection: Conexão ativa com o banco de dados.
    """
    return psycopg2.connect(
        dbname=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        sslmode=st.secrets["postgres"]["sslmode"]
    )

def inicializar_banco():
    """
    Inicializa as tabelas do banco de dados, caso ainda não existam.
    """
    comandos = [
        '''
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            data_cadastro TIMESTAMP,
            ultima_visita TIMESTAMP,
            observacoes TEXT
        )''',
        '''
        CREATE TABLE IF NOT EXISTS servicos (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco NUMERIC NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            descricao TEXT
        )''',
        '''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES clientes(id),
            servico_id INTEGER REFERENCES servicos(id),
            data_hora TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            pago BOOLEAN DEFAULT FALSE,
            metodo_pagamento TEXT,
            cliente_confirmado BOOLEAN DEFAULT FALSE,
            observacoes TEXT
        )''',
        '''
        CREATE TABLE IF NOT EXISTS custos (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor NUMERIC NOT NULL,
            tipo TEXT NOT NULL,
            data TIMESTAMP NOT NULL,
            categoria TEXT,
            recorrente BOOLEAN DEFAULT FALSE
        )'''
    ]
    conn = get_connection()
    cursor = conn.cursor()
    for cmd in comandos:
        cursor.execute(cmd)
    conn.commit()
    cursor.close()
    conn.close()

# Inicializar automaticamente se rodar o arquivo
if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados PostgreSQL inicializado!")
