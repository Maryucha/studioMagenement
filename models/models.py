# infra/db.py
"""
Módulo de infraestrutura responsável pela conexão com o banco PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    """
    Retorna uma nova conexão com o banco de dados PostgreSQL.

    Returns:
        psycopg2.extensions.connection: Conexão ativa com o banco de dados.
    """
    return psycopg2.connect(
        dbname="studio_finance",
        user="studio",
        password="studio123",
        host="localhost",
        port=5432
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


# models/models.py
"""
Módulo com as representações das entidades do domínio como dataclasses.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Cliente:
    id: int
    nome: str
    telefone: str
    email: str
    data_cadastro: datetime
    ultima_visita: Optional[datetime] = None
    observacoes: Optional[str] = None

@dataclass
class Servico:
    id: int
    nome: str
    categoria: str
    preco: float
    duracao_minutos: int
    descricao: Optional[str] = None

@dataclass
class Agendamento:
    id: int
    cliente_id: int
    servico_id: int
    data_hora: datetime
    status: str
    pago: bool = False
    metodo_pagamento: Optional[str] = None
    cliente_confirmado: bool = False
    observacoes: Optional[str] = None

@dataclass
class Custo:
    id: int
    descricao: str
    valor: float
    tipo: str
    data: datetime
    categoria: Optional[str] = None
    recorrente: bool = False
