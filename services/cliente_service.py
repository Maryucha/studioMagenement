"""
Serviço de Cliente

Este módulo implementa a lógica de negócio para operações com clientes.
Atua como intermediário entre o repositório de dados e a interface (front).
"""

from typing import Optional, Tuple
from datetime import datetime
from models.models import Cliente
from repositories import cliente_repo


def listar_clientes() -> list[Cliente]:
    """
    Lista todos os clientes cadastrados.

    Returns:
        list[Cliente]: Lista de objetos Cliente.
    """
    return cliente_repo.listar_clientes()


def buscar_cliente(cliente_id: int) -> Optional[Cliente]:
    """
    Busca um cliente pelo seu ID.

    Args:
        cliente_id (int): Identificador único do cliente.

    Returns:
        Optional[Cliente]: Objeto Cliente se encontrado, senão None.
    """
    return cliente_repo.buscar_cliente(cliente_id)


def adicionar_cliente(
    nome: str,
    telefone: str,
    email: str,
    observacoes: Optional[str] = None
) -> Optional[int]:
    """
    Adiciona um novo cliente ao banco de dados.

    Args:
        nome (str): Nome completo do cliente.
        telefone (str): Número de telefone.
        email (str): Endereço de e-mail.
        observacoes (Optional[str], optional): Observações adicionais. Padrão é None.

    Returns:
        Optional[int]: ID do cliente inserido, ou None se dados inválidos.
    """
    if not nome.strip():
        return None
    return cliente_repo.adicionar_cliente(nome, telefone, email, observacoes)


def atualizar_cliente(
    cliente_id: int,
    nome: str,
    telefone: str,
    email: str,
    observacoes: Optional[str] = None
) -> bool:
    """
    Atualiza os dados de um cliente existente.

    Args:
        cliente_id (int): Identificador do cliente.
        nome (str): Nome atualizado.
        telefone (str): Telefone atualizado.
        email (str): E-mail atualizado.
        observacoes (Optional[str], optional): Observações atualizadas. Padrão é None.

    Returns:
        bool: True se atualização foi bem-sucedida, False caso contrário.
    """
    cliente_existente = cliente_repo.buscar_cliente(cliente_id)
    if not cliente_existente:
        return False

    return cliente_repo.atualizar_cliente(cliente_id, nome, telefone, email, observacoes)


def excluir_cliente(cliente_id: int) -> Tuple[bool, str]:
    """
    Exclui um cliente, caso ele não possua agendamentos associados.

    Args:
        cliente_id (int): Identificador do cliente.

    Returns:
        Tuple[bool, str]: (Sucesso da operação, Mensagem explicativa)
    """
    return cliente_repo.excluir_cliente(cliente_id)
