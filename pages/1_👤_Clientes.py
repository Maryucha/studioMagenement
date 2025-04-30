"""
1_👤_Clientes.py

Autor: Maryucha M. Mariani
Data: 2025-04-29
Página de Gerenciamento de Clientes para o Studio.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import re

from services.cliente_service import (
    listar_clientes,
    buscar_cliente,
    adicionar_cliente,
    atualizar_cliente,
    excluir_cliente,
)
from utils.formatters import formatar_data_pt


# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Clientes", page_icon="👤", layout="wide")
st.title("👤 Gerenciamento de Clientes")


# -------------------------------
# Funções auxiliares
# -------------------------------
def limpar_formulario() -> None:
    """Limpa os campos do formulário no session_state."""
    st.session_state.cliente_id = None
    st.session_state.nome = ""
    st.session_state.telefone = ""
    st.session_state.email = ""
    st.session_state.observacoes = ""


def email_valido(email: str) -> bool:
    """
    Valida um endereço de e-mail com regex simples.

    Args:
        email (str): E-mail a ser validado.

    Returns:
        bool: True se o e-mail for válido.
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None


# -------------------------------
# Dados iniciais
# -------------------------------
clientes = listar_clientes()


# -------------------------------
# Sidebar - Formulário
# -------------------------------
with st.sidebar:
    st.header("📝 Cadastro de Cliente")

    cliente_id = st.session_state.get("cliente_id", None)
    nome = st.text_input("Nome completo", value=st.session_state.get("nome", ""))
    telefone = st.text_input("Telefone", value=st.session_state.get("telefone", ""))
    email = st.text_input("E-mail", value=st.session_state.get("email", ""))
    observacoes = st.text_area("Observações", value=st.session_state.get("observacoes", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar", use_container_width=True):
            limpar_formulario()
            st.rerun()

    with col2:
        if st.button("Salvar", type="primary", use_container_width=True):
            if not nome.strip():
                st.error("O nome do cliente é obrigatório!")
            elif email and not email_valido(email):
                st.error("E-mail inválido!")
            else:
                if cliente_id:
                    sucesso = atualizar_cliente(cliente_id, nome, telefone, email, observacoes)
                    if sucesso:
                        st.success(f"Cliente {nome} atualizado com sucesso!")
                    else:
                        st.error("Erro ao atualizar o cliente.")
                else:
                    novo_id = adicionar_cliente(nome, telefone, email, observacoes)
                    if novo_id:
                        st.success(f"Cliente {nome} cadastrado com sucesso!")
                    else:
                        st.error("Erro ao cadastrar o cliente.")

                limpar_formulario()
                st.rerun()


# -------------------------------
# Filtros
# -------------------------------
st.subheader("🔍 Filtrar Clientes")
col1, col2 = st.columns(2)

with col1:
    filtro_nome = st.text_input("Buscar por nome")

with col2:
    status_options = ["Todos", "Ativos", "Inativos (sem visita há mais de 90 dias)"]
    filtro_status = st.selectbox("Status", status_options)

# Criar DataFrame base
df_clientes = pd.DataFrame([{
    "id": c.id,
    "nome": c.nome,
    "telefone": c.telefone,
    "email": c.email,
    "data_cadastro": c.data_cadastro,
    "ultima_visita": c.ultima_visita,
    "observacoes": c.observacoes or ""
} for c in clientes])

# Aplicar filtros
if filtro_nome:
    df_clientes = df_clientes[df_clientes["nome"].str.lower().str.contains(filtro_nome.lower())]

if filtro_status == "Ativos":
    df_clientes = df_clientes[df_clientes["ultima_visita"].notna() & 
                              (datetime.now() - df_clientes["ultima_visita"]).dt.days <= 90]
elif filtro_status == "Inativos (sem visita há mais de 90 dias)":
    df_clientes = df_clientes[(df_clientes["ultima_visita"].isna()) | 
                              ((datetime.now() - df_clientes["ultima_visita"]).dt.days > 90)]

clientes_display = df_clientes.to_dict(orient="records")


# -------------------------------
# Tabela de Clientes
# -------------------------------
st.subheader(f"📋 Lista de Clientes ({len(clientes_display)})")

if not clientes_display:
    st.info("Nenhum cliente encontrado.")
else:
    df_visual = df_clientes.copy()
    df_visual["Data de Cadastro"] = df_visual["data_cadastro"].apply(
        lambda x: formatar_data_pt(x) if pd.notnull(x) else "-"
    )
    df_visual["Última Visita"] = df_visual["ultima_visita"].apply(
        lambda x: formatar_data_pt(x) if pd.notnull(x) else "Nunca"
    )
    df_visual = df_visual[["id", "nome", "telefone", "email", "Data de Cadastro", "Última Visita"]]
    df_visual = df_visual.set_index("id")

    editar_col, excluir_col = st.columns(2)

    with editar_col:
        selected_edit = st.selectbox(
            "Selecione um cliente para editar:",
            ["Nenhum"] + [f"{c['id']}: {c['nome']}" for c in clientes_display]
        )
        if selected_edit != "Nenhum":
            cliente_id = int(selected_edit.split(":")[0])
            cliente = buscar_cliente(cliente_id)
            if cliente:
                st.session_state.cliente_id = cliente.id
                st.session_state.nome = cliente.nome
                st.session_state.telefone = cliente.telefone
                st.session_state.email = cliente.email
                st.session_state.observacoes = cliente.observacoes or ""
                st.info(f"Cliente {cliente.nome} selecionado para edição.")

    with excluir_col:
        selected_delete = st.selectbox(
            "Selecione um cliente para excluir:",
            ["Nenhum"] + [f"{c['id']}: {c['nome']}" for c in clientes_display]
        )
        if selected_delete != "Nenhum":
            cliente_id = int(selected_delete.split(":")[0])
            st.warning("⚠ Esta ação é irreversível.")
            if st.checkbox("Confirmo que desejo excluir este cliente"):
                if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                    sucesso, mensagem = excluir_cliente(cliente_id)
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)

    st.dataframe(df_visual, use_container_width=True)


# -------------------------------
# Estatísticas
# -------------------------------
st.divider()
st.subheader("📊 Estatísticas")

col1, col2, col3 = st.columns(3)

with col1:
    total = len(clientes)
    st.metric("Total de Clientes", total)

with col2:
    ativos = len([
        c for c in clientes
        if c.ultima_visita and (datetime.now() - c.ultima_visita).days <= 90
    ])
    st.metric("Ativos (últimos 90 dias)", ativos)

with col3:
    percentual = (ativos / total * 100) if total > 0 else 0
    st.metric("% de Atividade", f"{percentual:.1f}%")
