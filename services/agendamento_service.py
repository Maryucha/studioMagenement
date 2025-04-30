"""
Serviço responsável pela lógica de negócio dos agendamentos.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from models.models import Agendamento
from repositories import agendamento_repo


def obter_agendamentos_filtrados(
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None
) -> List[Agendamento]:
    """
    Retorna uma lista de agendamentos filtrados por status e/ou período.

    Args:
        status (Optional[str]): Status do agendamento (pendente, realizado, cancelado).
        data_inicio (Optional[datetime]): Data inicial do período.
        data_fim (Optional[datetime]): Data final do período.

    Returns:
        List[Agendamento]: Lista de agendamentos que atendem aos filtros.
    """
    return agendamento_repo.listar_agendamentos(
        filtro_status=status,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


def deletar_agendamento(agendamento_id: int) -> bool:
    """
    Exclui um agendamento pelo ID.

    Args:
        agendamento_id (int): ID do agendamento a ser excluído.

    Returns:
        bool: True se excluído com sucesso, False caso contrário.
    """
    return agendamento_repo.excluir_agendamento(agendamento_id)


def buscar_agendamento_por_id(agendamento_id: int) -> Optional[Agendamento]:
    """
    Busca um agendamento específico pelo ID.

    Args:
        agendamento_id (int): ID do agendamento.

    Returns:
        Optional[Agendamento]: Agendamento encontrado ou None.
    """
    return agendamento_repo.buscar_agendamento(agendamento_id)


def atualizar_status_agendamento(agendamento_id: int, novo_status: str) -> bool:
    """
    Atualiza apenas o status de um agendamento.

    Args:
        agendamento_id (int): ID do agendamento.
        novo_status (str): Novo status (ex: "realizado").

    Returns:
        bool: True se atualizado com sucesso, False caso contrário.
    """
    agendamento = agendamento_repo.buscar_agendamento(agendamento_id)
    if not agendamento:
        return False

    return agendamento_repo.atualizar_agendamento(
        id=agendamento.id,
        cliente_id=agendamento.cliente_id,
        servico_id=agendamento.servico_id,
        data_hora=agendamento.data_hora,
        status=novo_status,
        observacoes=agendamento.observacoes
    )


def salvar_agendamento(
    modo: str,
    cliente_id: int,
    servico_id: int,
    data_hora: datetime,
    status: str,
    observacoes: Optional[str] = None,
    agendamento_id: Optional[int] = None
) -> Tuple[bool, str, Optional[datetime]]:
    """
    Cria ou edita um agendamento, garantindo que não haja sobreposição de horários.

    Args:
        modo (str): "criar" ou "editar".
        cliente_id (int): ID do cliente.
        servico_id (int): ID do serviço.
        data_hora (datetime): Data e hora desejada.
        status (str): Status do agendamento.
        observacoes (Optional[str]): Observações adicionais.
        agendamento_id (Optional[int]): ID do agendamento (obrigatório se editar).

    Returns:
        Tuple[bool, str, Optional[datetime]]: Sucesso, mensagem, sugestão de horário se houver conflito.
    """
    duracao = agendamento_repo.obter_duracao_servico(servico_id)
    if verificar_sobreposicao(servico_id, data_hora, duracao, agendamento_id):
        sugestao = sugerir_proximo_horario(servico_id, data_hora, duracao)
        return False, "Conflito: já existe um agendamento nesse horário.", sugestao

    if modo == "criar":
        novo_id = agendamento_repo.adicionar_agendamento(
            cliente_id=cliente_id,
            servico_id=servico_id,
            data_hora=data_hora,
            status=status,
            observacoes=observacoes
        )
        if novo_id:
            return True, "Agendamento criado com sucesso.", None
        return False, "Erro ao criar agendamento.", None

    elif modo == "editar" and agendamento_id:
        sucesso = agendamento_repo.atualizar_agendamento(
            id=agendamento_id,
            cliente_id=cliente_id,
            servico_id=servico_id,
            data_hora=data_hora,
            status=status,
            observacoes=observacoes
        )
        if sucesso:
            return True, "Agendamento atualizado com sucesso.", None
        return False, "Erro ao atualizar agendamento.", None

    return False, "Modo de operação inválido.", None


def verificar_sobreposicao(
    servico_id: int,
    inicio: datetime,
    duracao: int,
    agendamento_id: Optional[int] = None
) -> bool:
    """
    Verifica se o horário desejado entra em conflito com agendamentos existentes do mesmo serviço.

    Args:
        servico_id (int): ID do serviço.
        inicio (datetime): Data e hora de início.
        duracao (int): Duração do serviço em minutos.
        agendamento_id (Optional[int]): ID do agendamento atual (para excluir da verificação).

    Returns:
        bool: True se houver sobreposição, False caso contrário.
    """
    fim = inicio + timedelta(minutes=duracao)
    agendamentos = agendamento_repo.listar_agendamentos_por_servico(servico_id)
    for ag in agendamentos:
        if agendamento_id and ag.id == agendamento_id:
            continue
        ag_fim = ag.data_hora + timedelta(minutes=duracao)
        if inicio < ag_fim and fim > ag.data_hora:
            return True
    return False


def sugerir_proximo_horario(servico_id: int, inicio: datetime, duracao: int) -> Optional[datetime]:
    """
    Sugere o próximo horário disponível após um conflito.

    Args:
        servico_id (int): ID do serviço.
        inicio (datetime): Data e hora desejada.
        duracao (int): Duração do serviço em minutos.

    Returns:
        Optional[datetime]: Próximo horário disponível.
    """
    fim = inicio + timedelta(minutes=duracao)
    agendamentos = sorted(
        agendamento_repo.listar_agendamentos_por_servico(servico_id),
        key=lambda x: x.data_hora
    )
    for ag in agendamentos:
        ag_fim = ag.data_hora + timedelta(minutes=duracao)
        if fim <= ag.data_hora:
            return inicio
        inicio = max(inicio, ag_fim)
        fim = inicio + timedelta(minutes=duracao)
    return inicio
