# repositories/cliente_repo.py
"""
Repositório responsável por operações relacionadas a clientes.
"""
from infra.database import get_connection
from models.models import Cliente
from datetime import datetime
from typing import Optional

def adicionar_cliente(nome: str, telefone: str, email: str, observacoes: Optional[str] = None) -> int:
    """
    Insere um novo cliente no banco de dados.

    Args:
        nome (str): Nome do cliente.
        telefone (str): Telefone de contato.
        email (str): Endereço de e-mail.
        observacoes (Optional[str], optional): Observações adicionais.

    Returns:
        int: ID do cliente inserido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    data_cadastro = datetime.now()
    cursor.execute(
        """
        INSERT INTO clientes (nome, telefone, email, data_cadastro, observacoes)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (nome, telefone, email, data_cadastro, observacoes)
    )
    cliente_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return cliente_id

def listar_clientes() -> list[Cliente]:
    """
    Retorna todos os clientes cadastrados no banco.

    Returns:
        list[Cliente]: Lista de objetos Cliente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, telefone, email, data_cadastro, ultima_visita, observacoes
        FROM clientes
        ORDER BY nome
        """
    )
    rows = cursor.fetchall()
    clientes = [
        Cliente(
            id=r[0], nome=r[1], telefone=r[2], email=r[3],
            data_cadastro=r[4], ultima_visita=r[5], observacoes=r[6]
        ) for r in rows
    ]
    cursor.close()
    conn.close()
    return clientes

def atualizar_ultima_visita(cliente_id: int, data_hora: datetime, conn=None) -> None:
    """
    Atualiza a data da última visita de um cliente.

    Args:
        cliente_id (int): ID do cliente.
        data_hora (datetime): Data e hora da visita.
        conn (psycopg2 connection, optional): Conexão reutilizável.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE clientes
        SET ultima_visita = %s
        WHERE id = %s
        """,
        (data_hora, cliente_id)
    )

    if close_conn:
        conn.commit()
        cursor.close()
        conn.close()
        
def atualizar_cliente(cliente_id: int, nome: str, telefone: str, email: str, observacoes: Optional[str] = None) -> bool:
    """
    Atualiza os dados de um cliente existente.

    Args:
        cliente_id (int): ID do cliente a ser atualizado.
        nome (str): Novo nome.
        telefone (str): Novo telefone.
        email (str): Novo e-mail.
        observacoes (Optional[str], optional): Novas observações. Padrão é None.

    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE clientes
        SET nome = %s,
            telefone = %s,
            email = %s,
            observacoes = %s
        WHERE id = %s
        """,
        (nome, telefone, email, observacoes, cliente_id)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def excluir_cliente(cliente_id: int) -> tuple[bool, str]:
    """
    Exclui um cliente, se ele não possuir agendamentos associados.

    Args:
        cliente_id (int): ID do cliente a ser excluído.

    Returns:
        tuple[bool, str]: Resultado da operação e mensagem explicativa.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE cliente_id = %s", (cliente_id,))
    count = cursor.fetchone()[0]

    if count > 0:
        cursor.close()
        conn.close()
        return False, "Cliente possui agendamentos e não pode ser excluído"

    cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso, "Cliente excluído com sucesso"

def buscar_cliente(cliente_id: int) -> Optional[Cliente]:
    """
    Busca um cliente pelo seu ID.

    Args:
        cliente_id (int): ID do cliente.

    Returns:
        Optional[Cliente]: Objeto Cliente se encontrado, senão None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, telefone, email, data_cadastro, ultima_visita, observacoes
        FROM clientes
        WHERE id = %s
        """,
        (cliente_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return Cliente(
        id=row[0], nome=row[1], telefone=row[2], email=row[3],
        data_cadastro=row[4], ultima_visita=row[5], observacoes=row[6]
    )