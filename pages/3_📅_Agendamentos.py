"""
3_🗕️_Agendamentos.py


Página de Gerenciamento de Agendamentos para o Studio.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from services import agendamento_service
from repositories.cliente_repo import listar_clientes
from repositories.servico_repo import listar_servicos
from utils.formatters import (
    formatar_data_hora_pt,
    formatar_moeda_euro,
    status_agendamento,
)

# -------------------------------
# Dados principais
# -------------------------------
def carregar_dados():
    clientes = listar_clientes()
    servicos = listar_servicos()
    return clientes, servicos

def dicionarios_auxiliares(clientes, servicos):
    return {
        'cliente_nomes': {c.id: c.nome for c in clientes},
        'servico_nomes': {s.id: s.nome for s in servicos},
        'servico_precos': {s.id: s.preco for s in servicos},
        'servico_duracoes': {s.id: s.duracao_minutos for s in servicos},
    }

# -------------------------------
# Estatísticas
# -------------------------------
def mostrar_estatisticas(agendamentos):
    st.markdown("### 📊 Estatísticas Rápidas")
    total = len(agendamentos)
    pendentes = sum(1 for a in agendamentos if a.status == "pendente")
    realizados = sum(1 for a in agendamentos if a.status == "realizado")
    cancelados = sum(1 for a in agendamentos if a.status == "cancelado")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", total)
    col2.metric("Pendentes", pendentes)
    col3.metric("Realizados", realizados)
    col4.metric("Cancelados", cancelados)

# -------------------------------
# Listagem
# -------------------------------
def mostrar_lista_agendamentos(agendamentos, nomes):
    st.subheader("📋 Lista de Agendamentos")

    filtro = st.selectbox("Filtrar por período", ["Hoje", "7 dias", "30 dias", "Todos"])
    hoje = datetime.now().date()

    if filtro == "Hoje":
        agendamentos = [a for a in agendamentos if a.data_hora.date() == hoje]
    elif filtro == "7 dias":
        fim = hoje + timedelta(days=7)
        agendamentos = [a for a in agendamentos if hoje <= a.data_hora.date() <= fim]
    elif filtro == "30 dias":
        fim = hoje + timedelta(days=30)
        agendamentos = [a for a in agendamentos if hoje <= a.data_hora.date() <= fim]

    if not agendamentos:
        st.info("Nenhum agendamento encontrado para o filtro selecionado.")
        return

    df = pd.DataFrame([{
        "ID": a.id,
        "Data e Hora": formatar_data_hora_pt(a.data_hora),
        "Cliente": nomes['cliente_nomes'].get(a.cliente_id, f"Cliente {a.cliente_id}"),
        "Serviço": nomes['servico_nomes'].get(a.servico_id, f"Serviço {a.servico_id}"),
        "Valor": formatar_moeda_euro(nomes['servico_precos'].get(a.servico_id, 0)),
        "Status": a.status.capitalize(),
        "Observações": a.observacoes or "-"
    } for a in agendamentos]).sort_values(by="Data e Hora").set_index("ID")

    st.dataframe(df, use_container_width=True)
    mostrar_opcoes_status(agendamentos)

# -------------------------------
# Formulário lateral
# -------------------------------
def mostrar_formulario(clientes, servicos, nomes):
    """
    Exibe o formulário lateral para criar ou editar agendamentos.

    Args:
        clientes (List): Lista de clientes disponíveis.
        servicos (List): Lista de serviços disponíveis.
        nomes (dict): Dicionários auxiliares com nomes e durações.
    """
    with st.sidebar:
        st.header("📝 Cadastro de Agendamento")

        agendamento_id = st.session_state.get("agendamento_id", None)

        # Cliente
        cliente_options = ["Selecione um cliente..."] + [f"{c.id}: {c.nome}" for c in clientes]
        cliente_selecionado = st.selectbox("Cliente", cliente_options)
        cliente_id = None if cliente_selecionado == "Selecione um cliente..." else int(cliente_selecionado.split(":")[0])

        # Serviço
        servico_options = ["Selecione um serviço..."] + [
            f"{s.id}: {s.nome} - {formatar_moeda_euro(s.preco)}" for s in servicos
        ]
        servico_selecionado = st.selectbox("Serviço", servico_options)
        servico_id = None if servico_selecionado == "Selecione um serviço..." else int(servico_selecionado.split(":")[0])

        # Data, hora, status, observações
        data = st.date_input("Data", value=st.session_state.get("data", datetime.now()))
        hora = st.time_input("Hora", value=st.session_state.get("hora", datetime.now().time()))
        status = st.selectbox("Status", status_agendamento())
        observacoes = st.text_area("Observações", value=st.session_state.get("observacoes", ""))

        # Botões
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Limpar"):
                limpar_formulario()

        with col2:
            if st.button("Salvar", type="primary"):
                if not cliente_id:
                    st.error("Selecione um cliente!")
                    return
                if not servico_id:
                    st.error("Selecione um serviço!")
                    return

                data_hora = datetime.combine(data, hora)
                modo = "editar" if agendamento_id else "criar"

                sucesso, mensagem, sugestao = agendamento_service.salvar_agendamento(
                    modo=modo,
                    cliente_id=cliente_id,
                    servico_id=servico_id,
                    data_hora=data_hora,
                    status=status,
                    observacoes=observacoes,
                    agendamento_id=agendamento_id
                )

                if sucesso:
                    st.success(mensagem)
                    limpar_formulario()
                    st.rerun()
                else:
                    st.error(mensagem)
                    if sugestao:
                        st.info(f"Sugestão de horário: {sugestao.strftime('%H:%M')}")

# -------------------------------
# Limpeza de estado do formulário
# -------------------------------
def limpar_formulario():
    st.session_state.agendamento_id = None
    st.session_state.cliente_id = None
    st.session_state.servico_id = None
    st.session_state.data = datetime.now()
    st.session_state.hora = datetime.now().time()
    st.session_state.status = "pendente"
    st.session_state.observacoes = ""
 
# -------------------------------
# Opções de status
# -------------------------------
def mostrar_opcoes_status(agendamentos):
    st.subheader("🔄 Atualização Rápida de Status")
    pendentes = [a for a in agendamentos if a.status == "pendente"]

    col1, col2 = st.columns(2)

    with col1:
        selecionado = st.selectbox("Marcar como Realizado", ["Nenhum"] + [f"{a.id}: {formatar_data_hora_pt(a.data_hora)}" for a in pendentes], key="realizado")
        if selecionado != "Nenhum":
            ag_id = int(selecionado.split(":")[0])
            if st.button("Confirmar Realização", key="btn_realizado"):
                if agendamento_service.atualizar_status_agendamento(ag_id, "realizado"):
                    st.success("Marcado como realizado!")
                    st.rerun()

    with col2:
        selecionado = st.selectbox("Marcar como Cancelado", ["Nenhum"] + [f"{a.id}: {formatar_data_hora_pt(a.data_hora)}" for a in pendentes], key="cancelado")
        if selecionado != "Nenhum":
            ag_id = int(selecionado.split(":")[0])
            if st.button("Confirmar Cancelamento", key="btn_cancelado"):
                if agendamento_service.atualizar_status_agendamento(ag_id, "cancelado"):
                    st.success("Agendamento cancelado.")
                    st.rerun()

# -------------------------------
# Timeline do dia
# -------------------------------
def mostrar_timeline_dia():
    st.subheader("📆 Agenda por Data")
    data_agenda = st.date_input("Selecione uma data", value=datetime.now().date())

    agendamentos_do_dia = agendamento_service.obter_agendamentos_filtrados(
        data_inicio=data_agenda,
        data_fim=data_agenda
    )

    if not agendamentos_do_dia:
        st.info("Nenhum agendamento para esse dia.")
        return

    agendamentos_ordenados = sorted(agendamentos_do_dia, key=lambda a: a.data_hora)
    for ag in agendamentos_ordenados:
        st.write(f"- {formatar_data_hora_pt(ag.data_hora)} | {ag.status.capitalize()} | Cliente {ag.cliente_id}")

# -------------------------------
# Main
# -------------------------------
def main():
    st.set_page_config(page_title="Agendamentos", page_icon="🗕️", layout="wide")
    st.title("📅 Gerenciamento de Agendamentos")

    clientes, servicos = carregar_dados()
    nomes = dicionarios_auxiliares(clientes, servicos)

    mostrar_formulario(clientes, servicos, nomes)
    agendamentos = agendamento_service.obter_agendamentos_filtrados()
    mostrar_estatisticas(agendamentos)

    view = st.radio("Visualização:", ["Lista de Agendamentos", "Agenda por Data"], horizontal=True)
    if view == "Lista de Agendamentos":
        mostrar_lista_agendamentos(agendamentos, nomes)
    elif view == "Agenda por Data":
        mostrar_timeline_dia()

if __name__ == "__main__":
    main()
