"""
dashboard_service.py

Serviço responsável por gerar dados para o dashboard do sistema ProductionTracker.

Autor: Maryucha M. Mariani
Data: 2025-04-29
"""

from datetime import datetime, timedelta
from infra.database import get_connection
from utils.formatters import converter_para_euro


def obter_aniversariantes_mes() -> list[tuple[int, str]]:
    """
    Retorna até 3 clientes aleatórios, simulando aniversariantes do mês.

    Returns:
        list[tuple[int, str]]: Lista de até 3 tuplas contendo (id, nome) dos clientes.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, nome
        FROM clientes
        ORDER BY RANDOM()
        LIMIT 3
        """
    )
    aniversariantes = cursor.fetchall()
    cursor.close()
    conn.close()
    return aniversariantes


def resumo_studio() -> dict:
    """
    Gera um resumo estatístico e financeiro do estúdio, incluindo métricas do dia,
    semana e mês, além de alertas para cancelamentos e agendamentos pendentes.

    Returns:
        dict: Dicionário contendo:
            - total_clientes (int)
            - total_servicos (int)
            - agendamentos_pendentes (int)
            - agendamentos_hoje (int)
            - agendamentos_semana (int)
            - faturamento_mes (float)
            - faturamento_dia (float)
            - atendimentos_dia (int)
            - clientes_dia (int)
            - ticket_medio_dia (float)
            - alerta_cancelamentos (bool)
            - cancelamentos_mes (int)
            - alerta_pendentes (bool)
            - pendentes_atrasados (int)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Totais gerais
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM servicos")
    total_servicos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE status = 'pendente'")
    agendamentos_pendentes = cursor.fetchone()[0]

    hoje = datetime.now()
    inicio_mes = datetime(hoje.year, hoje.month, 1)
    fim_mes = datetime(hoje.year + 1, 1, 1) if hoje.month == 12 else datetime(hoje.year, hoje.month + 1, 1)

    cursor.execute(
        """
        SELECT SUM(s.preco)
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.status = 'realizado'
          AND a.data_hora >= %s AND a.data_hora < %s
        """,
        (inicio_mes, fim_mes)
    )
    faturamento_mes = cursor.fetchone()[0] or 0

    # Métricas do dia
    hoje_inicio = datetime(hoje.year, hoje.month, hoje.day)
    hoje_fim = hoje_inicio + timedelta(days=1)

    cursor.execute(
        "SELECT COUNT(*) FROM agendamentos WHERE data_hora >= %s AND data_hora < %s",
        (hoje_inicio, hoje_fim)
    )
    agendamentos_hoje = cursor.fetchone()[0]

    semana_inicio = hoje - timedelta(days=hoje.weekday())
    semana_fim = semana_inicio + timedelta(days=7)

    cursor.execute(
        "SELECT COUNT(*) FROM agendamentos WHERE data_hora >= %s AND data_hora < %s",
        (semana_inicio, semana_fim)
    )
    agendamentos_semana = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT SUM(s.preco), COUNT(DISTINCT a.id), COUNT(DISTINCT a.cliente_id)
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        WHERE a.status = 'realizado'
          AND a.data_hora >= %s AND a.data_hora < %s
        """,
        (hoje_inicio, hoje_fim)
    )
    faturamento_dia_row = cursor.fetchone()
    faturamento_dia = faturamento_dia_row[0] or 0
    atendimentos_dia = faturamento_dia_row[1] or 0
    clientes_dia = faturamento_dia_row[2] or 0
    ticket_medio_dia = faturamento_dia / atendimentos_dia if atendimentos_dia > 0 else 0

    # Alertas
    data_limite = hoje - timedelta(days=30)
    cursor.execute(
        """
        SELECT COUNT(*) FROM agendamentos
        WHERE status = 'cancelado' AND data_hora >= %s
        """,
        (data_limite,)
    )
    cancelamentos_mes = cursor.fetchone()[0]
    alerta_cancelamentos = cancelamentos_mes > 10

    cursor.execute(
        """
        SELECT COUNT(*) FROM agendamentos
        WHERE status = 'pendente' AND data_hora < %s
        """,
        (hoje,)
    )
    pendentes_atrasados = cursor.fetchone()[0]
    alerta_pendentes = pendentes_atrasados > 5

    cursor.close()
    conn.close()

    return {
        "total_clientes": total_clientes,
        "total_servicos": total_servicos,
        "agendamentos_pendentes": agendamentos_pendentes,
        "agendamentos_hoje": agendamentos_hoje,
        "agendamentos_semana": agendamentos_semana,
        "faturamento_mes": converter_para_euro(faturamento_mes),
        "faturamento_dia": converter_para_euro(faturamento_dia),
        "atendimentos_dia": atendimentos_dia,
        "clientes_dia": clientes_dia,
        "ticket_medio_dia": converter_para_euro(ticket_medio_dia),
        "alerta_cancelamentos": alerta_cancelamentos,
        "cancelamentos_mes": cancelamentos_mes,
        "alerta_pendentes": alerta_pendentes,
        "pendentes_atrasados": pendentes_atrasados
    }