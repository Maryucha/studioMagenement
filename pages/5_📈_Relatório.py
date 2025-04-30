"""
📈_Relatório.py
Autor: Maryucha M. Mariani
Data: 2025-04-29

Página de Relatório de Produção e Faturamento para o Studio.
"""

import streamlit as st
import plotly.express as px
import pandas as pd

from services.dashboard_report_service import (
    gerar_dataframe_base,
    filtrar_dataframe,
    calcular_custos_mes,
    calcular_metricas,
    gerar_csv
)
from utils.formatters import converter_para_euro

# -------------------------------
# Configuração da página
# -------------------------------
st.set_page_config(page_title="Relatório", page_icon="📈", layout="wide")
st.title("📈 Relatório de Produção e Faturamento")

# -------------------------------
# Carregamento de dados
# -------------------------------
df = gerar_dataframe_base()

if df.empty:
    st.info("Nenhum serviço realizado ainda.")
    st.stop()

# -------------------------------
# Filtros
# -------------------------------
st.sidebar.header("🎯 Filtros do Relatório")
profissionais = sorted(df['Profissional'].dropna().unique())
profissional_selecionado = st.sidebar.selectbox("👩‍🎨 Profissional", ["Todos"] + profissionais)
ano_selecionado = st.sidebar.selectbox("📅 Ano Base", sorted(df['Ano'].unique(), reverse=True))
mes_selecionado = st.sidebar.selectbox("🗓️ Mês Base", sorted(df[df['Ano'] == ano_selecionado]['Mês'].unique()))

comparar = st.sidebar.checkbox("🔁 Comparar com outro mês?")
ano_comp = mes_comp = None
if comparar:
    ano_comp = st.sidebar.selectbox("📅 Ano Comparação", sorted(df['Ano'].unique(), reverse=True), key="comp_ano")
    mes_comp = st.sidebar.selectbox("🗓️ Mês Comparação", sorted(df[df['Ano'] == ano_comp]['Mês'].unique()), key="comp_mes")

# -------------------------------
# Aplicar Filtros e Métricas
# -------------------------------
df_base = filtrar_dataframe(df, profissional_selecionado, ano_selecionado, mes_selecionado)
df_comp = filtrar_dataframe(df, profissional_selecionado, ano_comp, mes_comp) if comparar else None

custos = calcular_custos_mes(ano_selecionado, mes_selecionado)
metricas = calcular_metricas(df_base, custos)

# -------------------------------
# Métricas
# -------------------------------
st.divider()
col1, col2 = st.columns(2)

col1.metric("💰 Faturamento", f"€ {converter_para_euro(metricas['faturamento']):.2f}")
col1.metric("🎯 Atendimentos", len(df_base))
col1.metric("💳 Ticket Médio", f"€ {converter_para_euro(metricas['ticket_medio']):.2f}")
col1.metric("🏛️ Custos Fixos", f"€ {converter_para_euro(metricas['custos_fixos']):.2f}")

col2.metric("🎒 Custos Variáveis", f"€ {converter_para_euro(metricas['custos_variaveis']):.2f}")
col2.metric("📉 Total de Custos", f"€ {converter_para_euro(metricas['custos_totais']):.2f}")
col2.metric("💸 Lucro Líquido", f"€ {converter_para_euro(metricas['lucro_liquido']):.2f}")

# -------------------------------
# Comparação
# -------------------------------
if comparar and not df_comp.empty:
    st.divider()
    st.subheader("🔁 Comparação com Outro Mês")

    faturamento_comp = df_comp["Valor (R$)"].sum()
    qtd_comp = len(df_comp)

    col1, col2 = st.columns(2)
    col1.metric("💰 Faturamento Comparativo", f"€ {converter_para_euro(faturamento_comp):.2f}")
    col2.metric("🎯 Atendimentos Comparativo", qtd_comp)

# -------------------------------
# Tabela Detalhada
# -------------------------------
st.divider()
st.subheader("📋 Detalhamento de Serviços")
st.dataframe(df_base[["Data e Hora", "Cliente", "Serviço", "Profissional", "Valor (R$)"]], use_container_width=True)

# -------------------------------
# Gráficos
# -------------------------------
st.divider()
st.subheader("📊 Gráficos de Produção")

# Top 5 serviços
top_servicos = df_base["Serviço"].value_counts().head(5).reset_index()
top_servicos.columns = ["Serviço", "Quantidade"]
fig_top = px.bar(top_servicos, x="Serviço", y="Quantidade", color="Serviço", text_auto=True, title="🏆 Top 5 Serviços Realizados")
st.plotly_chart(fig_top, use_container_width=True)

# Frequência diária
dias_freq = df_base["Dia"].value_counts().sort_index().reset_index()
dias_freq.columns = ["Dia", "Atendimentos"]
fig_dias = px.line(dias_freq, x="Dia", y="Atendimentos", markers=True, title="📅 Atendimentos por Dia do Mês")
st.plotly_chart(fig_dias, use_container_width=True)

# Distribuição de custos
if custos[2] > 0:
    df_custos = pd.DataFrame([
        {"Tipo": "Fixo", "Valor": custos[0]},
        {"Tipo": "Variável", "Valor": custos[1]}
    ])
    fig_custos = px.pie(df_custos, names="Tipo", values="Valor", title="📊 Distribuição de Custos", hole=0.4)
    st.plotly_chart(fig_custos, use_container_width=True)

# -------------------------------
# Exportação
# -------------------------------
st.divider()
st.subheader("📥 Exportar Relatório")

csv, nome_arquivo = gerar_csv(df_base, ano_selecionado, mes_selecionado)
st.download_button(
    label="📄 Baixar CSV",
    data=csv,
    file_name=nome_arquivo,
    mime="text/csv"
)
