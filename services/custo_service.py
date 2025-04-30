"""
Serviço responsável pela lógica de negócios relacionada a custos.
"""

from typing import Optional, List
from datetime import datetime
from models.models import Custo
from repositories import custo_repo
import pandas as pd


def criar_custo(
    descricao: str,
    valor: float,
    tipo: str,
    data: datetime,
    categoria: Optional[str],
    recorrente: bool
) -> Optional[int]:
    """
    Cria um novo custo.

    Args:
        descricao (str): Descrição do custo.
        valor (float): Valor do custo.
        tipo (str): Tipo do custo (fixo ou variável).
        data (datetime): Data do custo.
        categoria (Optional[str]): Categoria do custo.
        recorrente (bool): Se é um custo recorrente.

    Returns:
        Optional[int]: ID do custo criado ou None em caso de erro.
    """
    try:
        return custo_repo.adicionar_custo(descricao, valor, tipo, data, categoria, recorrente)
    except Exception as e:
        print(f"Erro ao criar custo: {e}")
        return None


def editar_custo(
    custo_id: int,
    descricao: str,
    valor: float,
    tipo: str,
    data: datetime,
    categoria: Optional[str],
    recorrente: bool
) -> bool:
    """
    Atualiza um custo existente.

    Args:
        custo_id (int): ID do custo.
        descricao (str): Nova descrição.
        valor (float): Novo valor.
        tipo (str): Novo tipo.
        data (datetime): Nova data.
        categoria (Optional[str]): Nova categoria.
        recorrente (bool): Atualização de recorrência.

    Returns:
        bool: True se atualizado com sucesso, False caso contrário.
    """
    return custo_repo.atualizar_custo(custo_id, descricao, valor, tipo, data, categoria, recorrente)


def remover_custo(custo_id: int) -> bool:
    """
    Remove um custo do sistema.

    Args:
        custo_id (int): ID do custo.

    Returns:
        bool: True se removido com sucesso, False caso contrário.
    """
    return custo_repo.excluir_custo(custo_id)


def obter_custos(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    tipo: Optional[str] = None
) -> List[Custo]:
    """
    Lista os custos com filtros opcionais.

    Args:
        mes (Optional[int]): Mês para filtro.
        ano (Optional[int]): Ano para filtro.
        tipo (Optional[str]): Tipo de custo (fixo, variável).

    Returns:
        List[Custo]: Lista de custos.
    """
    return custo_repo.listar_custos(mes, ano, tipo)


def obter_custo_por_id(custo_id: int) -> Optional[Custo]:
    """
    Busca um custo pelo ID.

    Args:
        custo_id (int): ID do custo.

    Returns:
        Optional[Custo]: Custo correspondente ou None.
    """
    return custo_repo.buscar_custo(custo_id)

def filtrar_custos(
    custos: List[Custo],
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    tipo: Optional[str] = None
) -> List[Custo]:
    """
    Filtra uma lista de custos por ano, mês e tipo.

    Args:
        custos (List[Custo]): Lista de custos original.
        ano (Optional[int]): Ano a filtrar.
        mes (Optional[int]): Mês a filtrar.
        tipo (Optional[str]): Tipo de custo a filtrar.

    Returns:
        List[Custo]: Lista de custos filtrada.
    """
    filtrados = custos
    if ano:
        filtrados = [c for c in filtrados if c.data.year == ano]
    if mes:
        filtrados = [c for c in filtrados if c.data.month == mes]
    if tipo and tipo != "Todos":
        filtrados = [c for c in filtrados if c.tipo == tipo]
    return filtrados


def calcular_totais(custos: List[Custo]) -> dict:
    """
    Calcula totais gerais, fixos e variáveis.

    Args:
        custos (List[Custo]): Lista de custos.

    Returns:
        dict: Totais (geral, fixo, variável).
    """
    return {
        "total": sum(c.valor for c in custos),
        "fixo": sum(c.valor for c in custos if c.tipo == "fixo"),
        "variavel": sum(c.valor for c in custos if c.tipo == "variavel")
    }


def agrupar_por_categoria(custos: List[Custo]) -> pd.DataFrame:
    """
    Agrupa os custos por categoria e soma os valores.

    Args:
        custos (List[Custo]): Lista de custos.

    Returns:
        pd.DataFrame: DataFrame com colunas 'Categoria' e 'Valor'.
    """
    categorias = {}
    for c in custos:
        categorias[c.categoria] = categorias.get(c.categoria, 0) + c.valor
    return pd.DataFrame([{"Categoria": cat, "Valor": val} for cat, val in categorias.items()])