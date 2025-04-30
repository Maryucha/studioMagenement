"""
Home.py

Página inicial do sistema Studio Finance.

Autor: Maryucha M. Mariani
Data: 2025-04-30
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

from utils.contents.frases import frases_motivacionais
from services.dashboard import resumo_studio, obter_aniversariantes_mes
from repositories.agendamento_repo import obter_proximos_agendamentos
from utils.formatters import formatar_data_hora_pt, converter_para_euro

# -------------------------------
# Configuração da Página
# -------------------------------
st.set_page_config(
    page_title="Studio Finance",
    page_icon="💇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Estilo CSS Customizado
# -------------------------------
st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f8f9fa;
    }
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 90%;
        font-weight: 600;
        color: #fff;
        background-color: #d63384;
        border-radius: 0.35rem;
    }
    .card {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar
# -------------------------------
with st.sidebar:
    st.markdown("### ℹ️ Sobre o Sistema")
    st.markdown("""
    **Studio Finance**

    Sistema completo para studios de beleza:
    - Clientes e Serviços
    - Agendamentos
    - Custos Operacionais
    - Relatórios Financeiros

    Navegue pelo menu lateral para acessar as funcionalidades.
    """)
    st.caption("© 2025 Studio Finance")

# -------------------------------
# Cabeçalho
# -------------------------------
st.title("💇 Studio Finance")
st.subheader("Sistema de Gestão Financeira para Studios de Beleza")

# Frase motivacional do dia
st.markdown("---")
st.info(f'"{random.choice(frases_motivacionais)}"')

# -------------------------------
# Métricas Principais
# -------------------------------
st.markdown("---")
try:
    metricas = resumo_studio()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📊 Indicadores Gerais")
        st.metric("Clientes", metricas["total_clientes"])
        st.metric("Serviços", metricas["total_servicos"])
        st.metric("Pendentes", metricas["agendamentos_pendentes"])
        st.metric("Faturamento Mês", f"€ {metricas['faturamento_mes']:.2f}")

    with col2:
        st.markdown("### 🗓️ Agenda")
        st.metric("Hoje", metricas["agendamentos_hoje"])
        st.metric("Semana", metricas["agendamentos_semana"])

    with col3:
        st.markdown("### 💰 Hoje")
        st.metric("Faturamento", f"€ {metricas['faturamento_dia']:.2f}")
        st.metric("Atendidos", metricas["clientes_dia"])
        st.metric("Ticket Médio", f"€ {metricas['ticket_medio_dia']:.2f}")

    if metricas["alerta_cancelamentos"] or metricas["alerta_pendentes"]:
        st.warning("⚠️ Atenção com agendamentos e cancelamentos!")
except Exception as e:
    st.error(f"Erro ao carregar resumo do estúdio: {e}")
    st.stop()

# -------------------------------
# Agendamentos
# -------------------------------
st.markdown("---")
st.markdown("## 🗓️ Agendamentos")

periodo = st.selectbox("Período", ["Hoje", "Semana", "Mês", "Personalizado"], index=0)
if periodo == "Personalizado":
    data_inicio = st.date_input("Data inicial", datetime.now().date())
    data_fim = st.date_input("Data final", datetime.now().date() + timedelta(days=7))
    dias = (data_fim - data_inicio).days + 1
else:
    dias = {"Hoje": 1, "Semana": 7, "Mês": 30}.get(periodo, 7)

agendamentos = obter_proximos_agendamentos(dias)

if agendamentos:
    for agend in agendamentos:
        st.markdown(f"""
        <div class='card'>
            <b>{formatar_data_hora_pt(agend['data_hora'])}</b><br>
            Cliente: {agend['cliente_nome']}<br>
            Serviço: {agend['servico_nome']}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhum agendamento para o período selecionado.")

# -------------------------------
# Aniversariantes
# -------------------------------
st.markdown("---")
st.markdown("## 🎂 Aniversariantes do Mês")

aniversariantes = obter_aniversariantes_mes()
if aniversariantes:
    for _, nome in aniversariantes:
        st.markdown(f"""
        <div class='card'>
            <span class='badge'>🎉</span> <b>{nome}</b>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Nenhum aniversariante encontrado neste mês.")
