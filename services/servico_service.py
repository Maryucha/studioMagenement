"""
Módulo de serviços do sistema ProductionTracker.
Responsável por aplicar regras de negócio e intermediar
as operações entre a camada de repositório e a camada de apresentação.
"""

from typing import Optional, List, Tuple
from models.models import Servico
from repositories import servico_repo

def obter_servicos() -> List[Servico]:
    """
    Retorna todos os serviços cadastrados, ordenados por categoria e nome.

    Returns:
        List[Servico]: Lista de objetos Servico.
    """
    return servico_repo.listar_servicos()

def buscar_servico_por_id(servico_id: int) -> Optional[Servico]:
    """
    Busca um serviço pelo seu ID.

    Args:
        servico_id (int): ID do serviço desejado.

    Returns:
        Optional[Servico]: Objeto Servico encontrado, ou None se inexistente.
    """
    return servico_repo.buscar_servico(servico_id)

def cadastrar_servico(
    nome: str,
    categoria: str,
    preco: float,
    duracao_minutos: int,
    descricao: Optional[str] = None
) -> Optional[int]:
    """
    Cadastra um novo serviço no banco de dados após validação.

    Args:
        nome (str): Nome do serviço.
        categoria (str): Categoria do serviço (pode incluir profissional).
        preco (float): Preço do serviço em euros.
        duracao_minutos (int): Duração do serviço em minutos.
        descricao (Optional[str]): Texto descritivo opcional.

    Returns:
        Optional[int]: ID do serviço cadastrado, ou None se falhar na validação.
    """
    if not nome.strip() or preco <= 0:
        return None
    return servico_repo.adicionar_servico(nome, categoria, preco, duracao_minutos, descricao)

def atualizar_servico_existente(
    servico_id: int,
    nome: str,
    categoria: str,
    preco: float,
    duracao_minutos: int,
    descricao: Optional[str] = None
) -> bool:
    """
    Atualiza os dados de um serviço existente.

    Args:
        servico_id (int): ID do serviço a ser atualizado.
        nome (str): Novo nome do serviço.
        categoria (str): Nova categoria do serviço.
        preco (float): Novo preço.
        duracao_minutos (int): Nova duração.
        descricao (Optional[str]): Nova descrição, se houver.

    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário.
    """
    return servico_repo.atualizar_servico(servico_id, nome, categoria, preco, duracao_minutos, descricao)

def remover_servico(servico_id: int) -> Tuple[bool, str]:
    """
    Remove um serviço do banco de dados, caso não haja agendamentos associados.

    Args:
        servico_id (int): ID do serviço a ser removido.

    Returns:
        Tuple[bool, str]: Tupla com sucesso (True/False) e mensagem explicativa.
    """
    return servico_repo.excluir_servico(servico_id)
