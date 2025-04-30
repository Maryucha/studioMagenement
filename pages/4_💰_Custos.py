"""
4_💰_Custos.py

Autor: Maryucha M. Mariani
Data: 2025-04-29

Página de Gerenciamento de Custos para o Studio.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from services import custo_service
from utils.formatters import (
    formatar_data_pt,
    formatar_moeda_euro,
    tipos_custos,
    categorias_custos,
)

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Custos", page_icon="💰", layout="wide")
st.title("💰 Gerenciamento de Custos")

# Carrega os dados
todos_custos = custo_service.obter_custos()

# -------------------------------
# Barra lateral - Formulário de custo
# -------------------------------
with st.sidebar:
    st.header("📝 Cadastro de Custo")

    custo_id = st.session_state.get("custo_id", None)
    descricao = st.text_input("Descrição", value=st.session_state.get("descricao", ""))
    valor = st.number_input(
        "Valor (R$)", min_value=0.0,
        value=float(st.session_state.get("valor", 0)),
        format="%.2f", step=10.0
    )

    tipo = st.selectbox("Tipo", tipos_custos(), index=tipos_custos().index(st.session_state.get("tipo", "fixo")))
    categoria = st.selectbox("Categoria", categorias_custos(), index=categorias_custos().index(st.session_state.get("categoria", "Outros")))
    data = st.date_input("Data do custo", value=st.session_state.get("data", datetime.now()))
    recorrente = st.checkbox("Custo recorrente mensal", value=st.session_state.get("recorrente", False))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar", use_container_width=True):
            for campo, valor_padrao in {
                "custo_id": None, "descricao": "", "valor": 0,
                "tipo": "fixo", "categoria": "Outros",
                "data": datetime.now(), "recorrente": False
            }.items():
                st.session_state[campo] = valor_padrao
            st.rerun()

    with col2:
        if st.button("Salvar", type="primary", use_container_width=True):
            if not descricao:
                st.error("A descrição do custo é obrigatória!")
            elif valor <= 0:
                st.error("O valor deve ser maior que zero!")
            else:
                if custo_id:
                    sucesso = custo_service.editar_custo(custo_id, descricao, valor, tipo, data, categoria, recorrente)
                    if sucesso:
                        st.success(f"Custo {descricao} atualizado com sucesso!")
                    else:
                        st.error("Erro ao atualizar o custo.")
                else:
                    novo_id = custo_service.criar_custo(descricao, valor, tipo, data, categoria, recorrente)
                    if novo_id:
                        st.success(f"Custo {descricao} cadastrado com sucesso!")
                    else:
                        st.error("Erro ao cadastrar o custo.")

                st.session_state.clear()
                st.rerun()

# -------------------------------
# Filtros
# -------------------------------
st.subheader("🔍 Filtrar Custos")
col1, col2, col3 = st.columns(3)

with col1:
    anos = sorted({c.data.year for c in todos_custos}, reverse=True) or [datetime.now().year]
    ano_sel = st.selectbox("Ano", ["Todos"] + anos)
    ano_filtro = None if ano_sel == "Todos" else int(ano_sel)

with col2:
    meses_nomes = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    mes_sel = st.selectbox("Mês", ["Todos"] + meses_nomes)
    mes_filtro = None if mes_sel == "Todos" else meses_nomes.index(mes_sel) + 1

with col3:
    tipo_sel = st.selectbox("Tipo", ["Todos"] + tipos_custos())

# Aplica filtros e carrega dados filtrados
custos_filtrados = custo_service.filtrar_custos(
    todos_custos, ano=ano_filtro, mes=mes_filtro, tipo=tipo_sel
)

# -------------------------------
# Tabela de custos
# -------------------------------
st.subheader(f"📋 Lista de Custos ({len(custos_filtrados)})")

if not custos_filtrados:
    st.info("Nenhum custo encontrado para os filtros selecionados.")
else:
    df_custos = pd.DataFrame([{
        "ID": c.id,
        "Data": formatar_data_pt(c.data),
        "Descrição": c.descricao,
        "Categoria": c.categoria,
        "Tipo": c.tipo.capitalize(),
        "Recorrente": "Sim" if c.recorrente else "Não",
        "Valor": formatar_moeda_euro(c.valor)
    } for c in custos_filtrados]).sort_values(by="Data", ascending=False).set_index("ID")

    col1, col2 = st.columns(2)
    with col1:
        selected_edit = st.selectbox("Selecione um custo para editar:", ["Nenhum"] + [f"{c.id}: {c.descricao} - {formatar_moeda_euro(c.valor)}" for c in custos_filtrados])
        if selected_edit != "Nenhum":
            custo_id = int(selected_edit.split(":")[0])
            custo = custo_service.obter_custo_por_id(custo_id)
            if custo:
                st.session_state.update({
                    "custo_id": custo.id,
                    "descricao": custo.descricao,
                    "valor": custo.valor,
                    "tipo": custo.tipo,
                    "categoria": custo.categoria,
                    "data": custo.data.date(),
                    "recorrente": custo.recorrente
                })
                st.info(f"Custo {custo.descricao} selecionado para edição.")

    with col2:
        selected_delete = st.selectbox("Selecione um custo para excluir:", ["Nenhum"] + [f"{c.id}: {c.descricao} - {formatar_moeda_euro(c.valor)}" for c in custos_filtrados])
        if selected_delete != "Nenhum":
            custo_id = int(selected_delete.split(":")[0])
            if st.button("Confirmar Exclusão", type="primary", use_container_width=True):
                if custo_service.remover_custo(custo_id):
                    st.success("Custo excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao excluir o custo.")

    st.dataframe(df_custos, use_container_width=True)

# -------------------------------
# Resumo financeiro e gráfico
# -------------------------------
st.divider()
st.subheader("📊 Resumo Financeiro")

resumo = custo_service.calcular_totais(custos_filtrados)
col1, col2, col3 = st.columns(3)
col1.metric("Total de Custos", formatar_moeda_euro(resumo["total"]))
col2.metric("Custos Fixos", formatar_moeda_euro(resumo["fixo"]))
col3.metric("Custos Variáveis", formatar_moeda_euro(resumo["variavel"]))

st.subheader("Distribuição por Categoria")
df_cat = custo_service.agrupar_por_categoria(custos_filtrados)
if not df_cat.empty:
    fig = px.bar(df_cat, x="Categoria", y="Valor", color="Categoria", text_auto=True)
    fig.update_layout(title="Custos por Categoria")
    st.plotly_chart(fig, use_container_width=True)
    