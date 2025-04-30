"""

Autor: Maryucha M. Mariani
Data: 2025-04-29

Página de Gerenciamento de Serviços para o Studio.
Atualizada para utilizar a camada de serviços.
"""
import streamlit as st
import pandas as pd

from services.servico_service import (
    obter_servicos,
    cadastrar_servico,
    atualizar_servico_existente,
    remover_servico,
    buscar_servico_por_id
)
from utils.formatters import formatar_moeda_euro

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Serviços", page_icon="💇", layout="wide")
st.title("💇 Gerenciamento de Serviços")

# Carrega os dados de serviços
servicos = obter_servicos()

# -------------------------------
# Barra lateral - Formulário de serviço
# -------------------------------
with st.sidebar:
    st.header("📝 Cadastro de Serviço")

    servico_id = st.session_state.get("servico_id", None)
    nome = st.text_input("Nome do serviço", value=st.session_state.get("nome", ""))

    categorias = ["Unhas", "Massagem", "Sobrancelhas", "Depilação", "Pestanas", "Outro"]
    categoria = st.selectbox("Categoria", categorias, index=0 if not st.session_state.get("categoria") else categorias.index(st.session_state.get("categoria")))

    profissionais = ["Lidia", "Pamyla"]
    profissional = st.selectbox("Profissional", profissionais, index=0 if not st.session_state.get("profissional") else profissionais.index(st.session_state.get("profissional")))

    preco = st.number_input("Preço (€)", min_value=0.0, value=float(st.session_state.get("preco", 0)), format="%.2f", step=10.0)
    duracao_minutos = st.number_input("Duração (minutos)", min_value=15, value=int(st.session_state.get("duracao_minutos", 30)), step=15)

    descricao = st.text_area("Descrição", value=st.session_state.get("descricao", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar", use_container_width=True):
            st.session_state.servico_id = None
            st.session_state.nome = ""
            st.session_state.categoria = categorias[0]
            st.session_state.profissional = profissionais[0]
            st.session_state.preco = 0
            st.session_state.duracao_minutos = 30
            st.session_state.descricao = ""
            st.rerun()

    with col2:
        submit_button = st.button("Salvar", type="primary", use_container_width=True)

    if submit_button:
        if not nome:
            st.error("O nome do serviço é obrigatório!")
        elif preco <= 0:
            st.error("O preço deve ser maior que zero!")
        else:
            categoria_completa = f"{categoria} - {profissional}"
            if servico_id:
                if atualizar_servico_existente(servico_id, nome, categoria_completa, preco, duracao_minutos, descricao):
                    st.success(f"Serviço {nome} atualizado com sucesso!")
                else:
                    st.error("Erro ao atualizar o serviço.")
            else:
                novo_id = cadastrar_servico(nome, categoria_completa, preco, duracao_minutos, descricao)
                if novo_id:
                    st.success(f"Serviço {nome} cadastrado com sucesso!")
                else:
                    st.error("Erro ao cadastrar o serviço.")

            st.session_state.servico_id = None
            st.session_state.nome = ""
            st.session_state.categoria = categorias[0]
            st.session_state.profissional = profissionais[0]
            st.session_state.preco = 0
            st.session_state.duracao_minutos = 30
            st.session_state.descricao = ""
            st.rerun()

# -------------------------------
# Filtros e exibição de serviços
# -------------------------------
st.subheader("🔍 Filtrar Serviços")
col1, col2 = st.columns(2)
with col1:
    filtro_categoria = st.selectbox("Categoria", ["Todas"] + categorias)
with col2:
    filtro_profissional = st.selectbox("Profissional", ["Todos"] + profissionais)

if filtro_categoria != "Todas" or filtro_profissional != "Todos":
    servicos_filtrados = []
    for servico in servicos:
        partes = servico.categoria.split(" - ") if " - " in servico.categoria else [servico.categoria, ""]
        cat = partes[0]
        prof = partes[1] if len(partes) > 1 else ""
        if filtro_categoria != "Todas" and cat != filtro_categoria:
            continue
        if filtro_profissional != "Todos" and prof != filtro_profissional:
            continue
        servicos_filtrados.append(servico)
    servicos_display = servicos_filtrados
else:
    servicos_display = servicos

st.subheader(f"📋 Lista de Serviços ({len(servicos_display)})")

if not servicos_display:
    st.info("Nenhum serviço encontrado.")
else:
    df_servicos = pd.DataFrame([{
        "ID": s.id,
        "Nome": s.nome,
        "Categoria": s.categoria,
        "Preço": formatar_moeda_euro(s.preco),
        "Duração": f"{s.duracao_minutos} min",
        "Descrição": s.descricao if s.descricao else "-"
    } for s in servicos_display])
    df_servicos = df_servicos.set_index("ID")

    editar_col, excluir_col = st.columns(2)

    with editar_col:
        selected_edit = st.selectbox("Selecione um serviço para editar:", ["Nenhum"] + [f"{s.id}: {s.nome}" for s in servicos_display])
        if selected_edit != "Nenhum":
            servico_id = int(selected_edit.split(":")[0])
            servico = buscar_servico_por_id(servico_id)
            if servico:
                partes = servico.categoria.split(" - ") if " - " in servico.categoria else [servico.categoria, profissionais[0]]
                cat = partes[0]
                prof = partes[1] if len(partes) > 1 else profissionais[0]
                st.session_state.servico_id = servico.id
                st.session_state.nome = servico.nome
                st.session_state.categoria = cat if cat in categorias else categorias[-1]
                st.session_state.profissional = prof if prof in profissionais else profissionais[0]
                st.session_state.preco = servico.preco
                st.session_state.duracao_minutos = servico.duracao_minutos
                st.session_state.descricao = servico.descricao or ""
                st.info(f"Serviço {servico.nome} selecionado para edição. Utilize o formulário ao lado para editar.")

    with excluir_col:
        selected_delete = st.selectbox("Selecione um serviço para excluir:", ["Nenhum"] + [f"{s.id}: {s.nome}" for s in servicos_display])
        if selected_delete != "Nenhum":
            servico_id = int(selected_delete.split(":")[0])
            if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                sucesso, mensagem = remover_servico(servico_id)
                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)

    st.dataframe(df_servicos, use_container_width=True)

# Estatísticas
st.divider()
st.subheader("📊 Estatísticas")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Serviços", len(servicos))
with col2:
    if servicos:
        servico_mais_caro = max(servicos, key=lambda s: s.preco)
        st.metric("Serviço Mais Caro", formatar_moeda_euro(servico_mais_caro.preco))
    else:
        st.metric("Serviço Mais Caro", formatar_moeda_euro(0))
with col3:
    if servicos:
        duracao_media = sum(s.duracao_minutos for s in servicos) / len(servicos)
        st.metric("Duração Média", f"{duracao_media:.0f} min")
    else:
        st.metric("Duração Média", "0 min")