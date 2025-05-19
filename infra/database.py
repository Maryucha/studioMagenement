# infra/database.py
"""
Módulo de infraestrutura responsável pela conexão com o banco PostgreSQL.

Cenários de execução:
1. Local + Docker (APP_ENV=local_docker):
   - Usa variáveis LOCAL_* do .env
   - Útil para desenvolvimento com banco local

2. Local + Neon (APP_ENV=local_neon):
   - Usa variáveis NEON_* do .env
   - Útil para testar com banco de produção localmente

3. Cloud + Neon (APP_ENV=cloud ou não definido):
   - Usa st.secrets["database"]
   - Padrão para Streamlit Cloud
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import streamlit as st

# Força o carregamento do .env pela raiz do projeto
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

def get_connection():
    """
    Retorna uma conexão com o banco PostgreSQL baseada no ambiente de execução.
    
    APP_ENV:
    - local_docker: usa variáveis LOCAL_* do .env
    - local_neon: usa variáveis NEON_* do .env
    - cloud: usa st.secrets["database"]
    """
    app_env = os.getenv("APP_ENV", "cloud")

    if app_env == "local_docker":
        # Configuração para desenvolvimento local com Docker
        return psycopg2.connect(
            dbname=os.getenv("LOCAL_DB_NAME", "studio_finance"),
            user=os.getenv("LOCAL_DB_USER", "studio"),
            password=os.getenv("LOCAL_DB_PASSWORD", "studio123"),
            host=os.getenv("LOCAL_DB_HOST", "localhost"),
            port=int(os.getenv("LOCAL_DB_PORT", "5432")),
            sslmode=os.getenv("LOCAL_DB_SSLMODE", "prefer")
        )
    elif app_env == "local_neon":
        # Configuração para desenvolvimento local com Neon
        return psycopg2.connect(
            dbname=os.getenv("NEON_DB_NAME"),
            user=os.getenv("NEON_DB_USER"),
            password=os.getenv("NEON_DB_PASSWORD"),
            host=os.getenv("NEON_DB_HOST"),
            port=int(os.getenv("NEON_DB_PORT", "5432")),
            sslmode=os.getenv("NEON_DB_SSLMODE", "require")
        )
    else:
        # Configuração para Streamlit Cloud
        db_config = st.secrets["database"]
        return psycopg2.connect(
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=int(db_config.get("port", "5432")),
            sslmode=db_config.get("sslmode", "require")
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

def mostrar_conexao_atual():
    """
    Mostra as configurações atuais de conexão (sem dados sensíveis).
    """
    app_env = os.getenv("APP_ENV", "cloud")
    print(f"\nAmbiente atual: {app_env}")
    
    if app_env == "local_docker":
        print("Conectando ao Docker local:")
        print(f"- Database: {os.getenv('LOCAL_DB_NAME', 'studio_finance')}")
        print(f"- Host: {os.getenv('LOCAL_DB_HOST', 'localhost')}")
        print(f"- Porta: {os.getenv('LOCAL_DB_PORT', '5432')}")
    elif app_env == "local_neon":
        print("Conectando ao Neon (local):")
        print(f"- Database: {os.getenv('NEON_DB_NAME')}")
        print(f"- Host: {os.getenv('NEON_DB_HOST')}")
    else:
        print("Conectando via Streamlit Cloud:")
        if "database" in st.secrets:
            db_config = st.secrets["database"]
            print(f"- Database: {db_config.get('dbname')}")
            print(f"- Host: {db_config.get('host')}")
        else:
            print("⚠️ Secrets não encontrados!")

if __name__ == "__main__":
    mostrar_conexao_atual()
    inicializar_banco()
    print("Banco de dados PostgreSQL inicializado!")
