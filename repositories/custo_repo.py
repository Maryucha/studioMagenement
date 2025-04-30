# repositories/custo_repo.py
"""
Repositório responsável por operações relacionadas a custos.
"""
from infra.database import get_connection
from models.models import Custo
from typing import Optional, List
from datetime import datetime

def adicionar_custo(
    descricao: str,
    valor: float,
    tipo: str,
    data: datetime,
    categoria: Optional[str] = None,
    recorrente: bool = False
) -> int:
    """
    Insere um novo custo no banco de dados.

    Returns:
        int: ID do custo criado.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO custos (descricao, valor, tipo, data, categoria, recorrente)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (descricao, valor, tipo, data, categoria, recorrente)
    )
    custo_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return custo_id

def atualizar_custo(
    id: int,
    descricao: str,
    valor: float,
    tipo: str,
    data: datetime,
    categoria: Optional[str] = None,
    recorrente: bool = False
) -> bool:
    """
    Atualiza os dados de um custo existente.

    Returns:
        bool: True se atualizado, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE custos
        SET descricao=%s, valor=%s, tipo=%s, data=%s, categoria=%s, recorrente=%s
        WHERE id=%s
        """,
        (descricao, valor, tipo, data, categoria, recorrente, id)
    )
    conn.commit()
    atualizado = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return atualizado

def excluir_custo(id: int) -> bool:
    """
    Exclui um custo pelo ID.

    Returns:
        bool: True se removido, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custos WHERE id=%s", (id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def listar_custos(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    tipo: Optional[str] = None
) -> List[Custo]:
    """
    Lista custos com filtros opcionais de mês, ano e tipo.

    Returns:
        List[Custo]: Lista de custos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT id, descricao, valor, tipo, data, categoria, recorrente FROM custos"
    params = []
    conditions = []

    if mes and ano:
        data_inicio = f"{ano}-{mes:02d}-01"
        if mes == 12:
            data_fim = f"{ano + 1}-01-01"
        else:
            data_fim = f"{ano}-{mes + 1:02d}-01"
        conditions.append("(data >= %s AND data < %s)")
        params.extend([data_inicio, data_fim])
    elif mes:
        conditions.append("EXTRACT(MONTH FROM data) = %s")
        params.append(mes)
    elif ano:
        conditions.append("EXTRACT(YEAR FROM data) = %s")
        params.append(ano)

    if tipo:
        conditions.append("tipo = %s")
        params.append(tipo)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY data DESC"
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    custos = [
        Custo(
            id=r[0], descricao=r[1], valor=r[2], tipo=r[3],
            data=r[4], categoria=r[5], recorrente=r[6]
        ) for r in rows
    ]
    cursor.close()
    conn.close()
    return custos

def buscar_custo(id: int) -> Optional[Custo]:
    """
    Busca um custo pelo ID.

    Returns:
        Optional[Custo]: Custo encontrado ou None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, descricao, valor, tipo, data, categoria, recorrente
        FROM custos
        WHERE id=%s
        """,
        (id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return Custo(
        id=row[0], descricao=row[1], valor=row[2], tipo=row[3],
        data=row[4], categoria=row[5], recorrente=row[6]
    )
