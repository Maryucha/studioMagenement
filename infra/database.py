# infra/database.py
"""
Módulo de infraestrutura responsável pela conexão com o banco PostgreSQL (via Neon)
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st

def get_connection():
    """
    Retorna uma nova conexão com o banco de dados PostgreSQL (compatível com Streamlit Cloud e Neon).
    Prioriza st.secrets['database'], mas permite fallback para variáveis de ambiente.
    """
    if "database" in st.secrets:
        db_config = st.secrets["database"]
        return psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config.get("port", 5432),
            sslmode=db_config.get("sslmode", "require")
        )
    else:
        # Fallback para variáveis de ambiente (útil para testes locais)
        return psycopg2.connect(
            dbname=os.environ.get("DB_NAME", "studio_finance"),
            user=os.environ.get("DB_USER", "studio"),
            password=os.environ.get("DB_PASSWORD", "studio123"),
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", 5432),
            sslmode=os.environ.get("DB_SSLMODE", "require")
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
