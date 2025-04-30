# repositories/servico_repo.py
"""
Repositório responsável por operações relacionadas a serviços.
"""
from infra.database import get_connection
from models.models import Servico
from typing import Optional

def adicionar_servico(nome: str, categoria: str, preco: float, duracao_minutos: int, descricao: Optional[str] = None) -> int:
    """
    Insere um novo serviço no banco de dados.

    Args:
        nome (str): Nome do serviço.
        categoria (str): Categoria do serviço.
        preco (float): Preço do serviço.
        duracao_minutos (int): Duração em minutos.
        descricao (Optional[str]): Descrição adicional.

    Returns:
        int: ID do serviço inserido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO servicos (nome, categoria, preco, duracao_minutos, descricao)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (nome, categoria, preco, duracao_minutos, descricao)
    )
    servico_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return servico_id

def atualizar_servico(id: int, nome: str, categoria: str, preco: float, duracao_minutos: int, descricao: Optional[str] = None) -> bool:
    """
    Atualiza os dados de um serviço existente.

    Args:
        id (int): ID do serviço.
        nome (str): Nome do serviço.
        categoria (str): Categoria do serviço.
        preco (float): Preço do serviço.
        duracao_minutos (int): Duração em minutos.
        descricao (Optional[str]): Descrição do serviço.

    Returns:
        bool: True se o serviço foi atualizado, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE servicos
        SET nome = %s, categoria = %s, preco = %s, duracao_minutos = %s, descricao = %s
        WHERE id = %s
        """,
        (nome, categoria, preco, duracao_minutos, descricao, id)
    )
    conn.commit()
    atualizado = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return atualizado

def excluir_servico(servico_id: int) -> tuple[bool, str]:
    """
    Exclui um serviço, se não houver agendamentos associados a ele.

    Args:
        servico_id (int): ID do serviço a ser excluído.

    Returns:
        tuple[bool, str]: Resultado e mensagem.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE servico_id = %s", (servico_id,))
    count = cursor.fetchone()[0]
    if count > 0:
        cursor.close()
        conn.close()
        return False, "Serviço possui agendamentos e não pode ser excluído"

    cursor.execute("DELETE FROM servicos WHERE id = %s", (servico_id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso, "Serviço excluído com sucesso"

def listar_servicos() -> list[Servico]:
    """
    Retorna todos os serviços cadastrados.

    Returns:
        list[Servico]: Lista de serviços.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, categoria, preco, duracao_minutos, descricao
        FROM servicos
        ORDER BY categoria, nome
        """
    )
    rows = cursor.fetchall()
    servicos = [
        Servico(
            id=r[0], nome=r[1], categoria=r[2], preco=r[3],
            duracao_minutos=r[4], descricao=r[5]
        ) for r in rows
    ]
    cursor.close()
    conn.close()
    return servicos

def buscar_servico(servico_id: int) -> Optional[Servico]:
    """
    Retorna um serviço pelo ID.

    Args:
        servico_id (int): ID do serviço.

    Returns:
        Optional[Servico]: Serviço encontrado ou None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome, categoria, preco, duracao_minutos, descricao
        FROM servicos
        WHERE id = %s
        """,
        (servico_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return Servico(
        id=row[0], nome=row[1], categoria=row[2], preco=row[3],
        duracao_minutos=row[4], descricao=row[5]
    )
