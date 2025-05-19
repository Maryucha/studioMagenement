"""
dashboard_report_service.py

Módulo de serviços para geração de dados e métricas do relatório de produção e faturamento.

Autor: Maryucha M. Mariani
Data: 2025-04-29
"""

from typing import Tuple, Dict
import pandas as pd

from repositories.cliente_repo import listar_clientes
from repositories.servico_repo import listar_servicos
from repositories.agendamento_repo import listar_agendamentos
from repositories.custo_repo import listar_custos


def gerar_dataframe_base() -> pd.DataFrame:
    """
    Gera um DataFrame base contendo informações de agendamentos realizados.

    Returns:
        pd.DataFrame: DataFrame com colunas: Cliente, Serviço, Profissional, Data e Hora, Valor, Ano, Mês, Dia.
    """
    agendamentos = listar_agendamentos()
    servicos = listar_servicos()
    clientes = listar_clientes()

    servico_precos = {s.id: s.preco for s in servicos}
    servico_nomes = {s.id: s.nome for s in servicos}
    servico_categorias = {s.id: s.categoria for s in servicos}
    cliente_nomes = {c.id: c.nome for c in clientes}

    realizados = [a for a in agendamentos if a.status == "realizado"]

    df = pd.DataFrame([{
        "Cliente": cliente_nomes.get(a.cliente_id, "Cliente não encontrado"),
        "Serviço": servico_nomes.get(a.servico_id, "Serviço não encontrado"),
        "Profissional": servico_categorias.get(a.servico_id, "Não definido"),
        "Data e Hora": a.data_hora,
        "Valor (R$)": servico_precos.get(a.servico_id, 0)
    } for a in realizados])

    # Garante que as colunas existam mesmo se o DataFrame estiver vazio
    if df.empty:
        df = pd.DataFrame(columns=[
            "Cliente", "Serviço", "Profissional", "Data e Hora", "Valor (R$)", "Ano", "Mês", "Dia"
        ])
    else:
        df["Ano"] = df["Data e Hora"].dt.year
        df["Mês"] = df["Data e Hora"].dt.month
        df["Dia"] = df["Data e Hora"].dt.day

    return df


def filtrar_dataframe(df: pd.DataFrame, profissional: str, ano: int, mes: int) -> pd.DataFrame:
    """
    Aplica os filtros de profissional, ano e mês ao DataFrame base.

    Args:
        df (pd.DataFrame): DataFrame base.
        profissional (str): Nome do profissional ou "Todos".
        ano (int): Ano selecionado.
        mes (int): Mês selecionado.

    Returns:
        pd.DataFrame: DataFrame filtrado.
    """
    if profissional != "Todos":
        df = df[df["Profissional"] == profissional]
    return df[(df["Ano"] == ano) & (df["Mês"] == mes)]


def calcular_custos_mes(ano: int, mes: int) -> Tuple[float, float, float]:
    """
    Calcula os custos fixos, variáveis e totais do mês.

    Args:
        ano (int): Ano base.
        mes (int): Mês base.

    Returns:
        Tuple[float, float, float]: Custos fixos, variáveis e total.
    """
    custos = listar_custos()
    custos_mes = [c for c in custos if c.data.year == ano and c.data.month == mes]

    fixos = sum(c.valor for c in custos_mes if c.tipo == "fixo")
    variaveis = sum(c.valor for c in custos_mes if c.tipo == "variavel")
    total = fixos + variaveis

    return fixos, variaveis, total


def calcular_metricas(df_base: pd.DataFrame, custos: Tuple[float, float, float]) -> Dict[str, float]:
    """
    Calcula métricas principais do relatório como faturamento, lucro e ticket médio.

    Args:
        df_base (pd.DataFrame): DataFrame filtrado.
        custos (Tuple[float, float, float]): Custos fixos, variáveis e total.

    Returns:
        Dict[str, float]: Dicionário com métricas financeiras.
    """
    faturamento = df_base["Valor (R$)"].sum()
    qtd = len(df_base)
    ticket_medio = faturamento / qtd if qtd else 0
    lucro = faturamento - custos[2]

    return {
        "faturamento": faturamento,
        "ticket_medio": ticket_medio,
        "lucro_liquido": lucro,
        "custos_fixos": custos[0],
        "custos_variaveis": custos[1],
        "custos_totais": custos[2]
    }


def gerar_csv(df: pd.DataFrame, ano: int, mes: int) -> Tuple[str, str]:
    """
    Gera o conteúdo e o nome do arquivo CSV para exportação.

    Args:
        df (pd.DataFrame): DataFrame filtrado.
        ano (int): Ano selecionado.
        mes (int): Mês selecionado.

    Returns:
        Tuple[str, str]: Conteúdo CSV codificado e nome do arquivo.
    """
    csv = df.to_csv(index=False, sep=";").encode("utf-8")
    nome_arquivo = f"relatorio_faturamento_{ano}_{mes}.csv"
    return csv, nome_arquivo
