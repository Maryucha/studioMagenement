# repositories/agendamento_repo.py
"""

Autor: Maryucha M. Mariani
Data: 2025-04-29

Repositório responsável por operações relacionadas a agendamentos.
"""
from infra.database import get_connection
from models.models import Agendamento
from repositories.cliente_repo import atualizar_ultima_visita
from typing import Optional, List
from datetime import datetime
from datetime import datetime, timedelta

def adicionar_agendamento(
    cliente_id: int,
    servico_id: int,
    data_hora: datetime,
    status: str = "pendente",
    pago: bool = False,
    metodo_pagamento: Optional[str] = None,
    cliente_confirmado: bool = False,
    observacoes: Optional[str] = None
) -> int:
    """
    Insere um novo agendamento no banco de dados.

    Returns:
        int: ID do agendamento criado.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO agendamentos (cliente_id, servico_id, data_hora, status, pago, metodo_pagamento, cliente_confirmado, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (cliente_id, servico_id, data_hora, status, pago, metodo_pagamento, cliente_confirmado, observacoes)
    )
    agendamento_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return agendamento_id

def atualizar_agendamento(
    id: int,
    cliente_id: int,
    servico_id: int,
    data_hora: datetime,
    status: str,
    pago: bool = False,
    metodo_pagamento: Optional[str] = None,
    cliente_confirmado: bool = False,
    observacoes: Optional[str] = None
) -> bool:
    """
    Atualiza um agendamento existente e atualiza a última visita, se realizado.

    Returns:
        bool: True se atualizado, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE agendamentos
        SET cliente_id=%s, servico_id=%s, data_hora=%s, status=%s,
            pago=%s, metodo_pagamento=%s, cliente_confirmado=%s, observacoes=%s
        WHERE id=%s
        """,
        (cliente_id, servico_id, data_hora, status, pago, metodo_pagamento, cliente_confirmado, observacoes, id)
    )
    if status == "realizado":
        atualizar_ultima_visita(cliente_id, data_hora, conn)
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def confirmar_cliente_chegou(id: int, confirmado: bool = True) -> bool:
    """
    Marca o agendamento como confirmado.

    Returns:
        bool: True se confirmado, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE agendamentos SET cliente_confirmado=%s WHERE id=%s", (confirmado, id))
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def registrar_pagamento(id: int, pago: bool = True, metodo_pagamento: Optional[str] = None) -> bool:
    """
    Registra o pagamento de um agendamento.

    Returns:
        bool: True se atualizado, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE agendamentos SET pago=%s, metodo_pagamento=%s WHERE id=%s",
        (pago, metodo_pagamento, id)
    )
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def excluir_agendamento(id: int) -> bool:
    """
    Remove um agendamento pelo ID.

    Returns:
        bool: True se removido, False caso contrário.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id=%s", (id,))
    conn.commit()
    sucesso = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return sucesso

def listar_agendamentos(
    filtro_status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[Agendamento]:
    """
    Lista agendamentos com filtros opcionais de status e período.

    Returns:
        List[Agendamento]: Lista de agendamentos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id, cliente_id, servico_id, data_hora, status,
           pago, metodo_pagamento, cliente_confirmado, observacoes
    FROM agendamentos
    """
    conditions = []
    params = []
    if filtro_status:
        conditions.append("status = %s")
        params.append(filtro_status)
    if data_inicio:
        conditions.append("data_hora >= %s")
        params.append(data_inicio)
    if data_fim:
        conditions.append("data_hora <= %s")
        params.append(data_fim)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY data_hora DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    agendamentos = [
        Agendamento(
            id=r[0], cliente_id=r[1], servico_id=r[2], data_hora=r[3],
            status=r[4], pago=r[5], metodo_pagamento=r[6],
            cliente_confirmado=r[7], observacoes=r[8]
        ) for r in rows
    ]
    cursor.close()
    conn.close()
    return agendamentos

def buscar_agendamento(id: int) -> Optional[Agendamento]:
    """
    Retorna um agendamento pelo ID.

    Returns:
        Optional[Agendamento]: Agendamento encontrado ou None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, cliente_id, servico_id, data_hora, status,
               pago, metodo_pagamento, cliente_confirmado, observacoes
        FROM agendamentos
        WHERE id = %s
        """,
        (id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return Agendamento(
        id=row[0], cliente_id=row[1], servico_id=row[2], data_hora=row[3],
        status=row[4], pago=row[5], metodo_pagamento=row[6],
        cliente_confirmado=row[7], observacoes=row[8]
    )

def obter_proximos_agendamentos(dias=7):
    """Retorna os próximos agendamentos dentro do período especificado"""
    conn = get_connection()
    cursor = conn.cursor()

    hoje = datetime.now()
    limite = hoje + timedelta(days=dias)

    cursor.execute(
        """
        SELECT a.id, a.cliente_id, a.servico_id, a.data_hora, a.status,
               a.pago, a.cliente_confirmado, c.nome, c.telefone, s.nome, s.categoria
        FROM agendamentos a
        JOIN clientes c ON a.cliente_id = c.id
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.data_hora >= %s AND a.data_hora <= %s
          AND a.status = 'pendente'
        ORDER BY a.data_hora
        """,
        (hoje, limite)
    )
    agendamentos = cursor.fetchall()
    cursor.close()
    conn.close()

    resultado = []
    for ag in agendamentos:
        resultado.append({
            "id": ag[0],
            "cliente_id": ag[1],
            "servico_id": ag[2],
            "data_hora": ag[3],
            "status": ag[4],
            "pago": bool(ag[5]),
            "cliente_confirmado": bool(ag[6]),
            "cliente_nome": ag[7],
            "cliente_telefone": ag[8],
            "servico_nome": ag[9],
            "categoria": ag[10]
        })
    return resultado

def listar_agendamentos_por_servico(servico_id: int) -> List[Agendamento]:
    """
    Retorna todos os agendamentos de um determinado serviço.

    Args:
        servico_id (int): ID do serviço (profissional).

    Returns:
        List[Agendamento]: Lista de agendamentos associados ao serviço.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, cliente_id, servico_id, data_hora, status,
               pago, metodo_pagamento, cliente_confirmado, observacoes
        FROM agendamentos
        WHERE servico_id = %s
        ORDER BY data_hora
    """, (servico_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        Agendamento(
            id=r[0], cliente_id=r[1], servico_id=r[2], data_hora=r[3],
            status=r[4], pago=r[5], metodo_pagamento=r[6],
            cliente_confirmado=r[7], observacoes=r[8]
        ) for r in rows
    ]

def obter_duracao_servico(servico_id: int) -> int:
    """
    Retorna a duração, em minutos, de um serviço específico.

    Args:
        servico_id (int): ID do serviço.

    Returns:
        int: Duração do serviço em minutos.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT duracao_minutos FROM servicos WHERE id = %s", (servico_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    return row[0] if row and row[0] else 60  # 60 minutos como fallback
