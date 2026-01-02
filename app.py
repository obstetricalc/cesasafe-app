import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="ObstetriCalc: Apoio à Decisão", page_icon="👶", layout="wide")

def main():
    st.title("👶 ObstetriCalc: Relatório de Indicação de Via de Parto")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é auxiliar. A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    
    st.markdown("---")

    # --- 1. DADOS CLÍNICOS E DATAÇÃO ---
    st.header("1. Dados Clínicos e Obstétricos")
    
    # Linha 1: Nome e Idade
    c_dados1, c_dados2 = st.columns([2, 1])
    with c_dados1:
        nome = st.text_input("Nome da Paciente")
    with c_dados2:
        idade = st.number_input("Idade", min_value=10, max_value=60, value=25)

    # Linha 2: Histórico Obstétrico (G P A)
    st.markdown("**Histórico Obstétrico:**")
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0)
    with col_pc:
        partos_cesareos = st.number_input("PC (Cesáreas)", min_value=0, value=0)
    with col_a:
        abortos = st.number_input("A (Abortos)", min_value=0, value=0)

    # Alerta de Cesárea Prévia (Condicional)
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo foi a última cesárea?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("---")
    
    # --- DATAÇÃO (LAYOUT DO DESENHO) ---
    st.subheader("📅 Datação da Gestação")

    # LINHA A: DUM -> IG -> DPP
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    with col_dum:
        dum = st.date_input("DUM (Data Última Menstruação)", value=date.today())
    
    # Cálculo automático pela DUM
    dias_gest = (date.today() - dum).days
    # Evitar números negativos se data for futura
    if dias_gest < 0: dias_gest = 0
    ig_sem = dias_gest // 7
    ig_dias = dias_gest % 7
    dpp_calc = dum + timedelta(days=280)

    with col_ig_dum:
        st.metric("IG (pela DUM)", f"{ig_sem}s e {ig_dias}d")
    with col_dpp_dum:
        st.metric("DPP (Provável)", dpp_calc.strftime('%d/%m/%Y'))

    # LINHA B: DPPeco -> IGeco
    col_eco, col_ig_eco, col_vazio = st.columns(3)
    
    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (DPP Eco)", value=date.today())
    
    # Cálculo automático pela USG (Retroativo)
    dt_concepcao_eco = dpp_eco - timedelta(days=280)
    dias_gest_eco = (date.today() - dt_concepcao_eco).days
    if dias_gest_eco < 0: dias_gest_eco = 0
    ig_sem_eco = dias_gest_eco // 7
    ig_dias_eco = dias_gest_eco % 7

    with col_ig_eco:
        st.metric("IG (pela USG)", f"{ig_sem_eco}s e {ig_dias_eco}d")
    
    # Definindo qual IG usar para as sugestões finais (usando DUM como padrão para lógica)
    ig_final_semanas = ig_sem 

    st.markdown("---")

    # --- 2. ÍNDICE DE BISHOP ---
    st.header("2. Índice de Bishop")
    st.caption("Avaliação para sucesso de indução vs. Cesárea")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        dilatacao = st.selectbox("Dilatação (cm)", options=[0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥ 5 cm (3)"][x])
    with c2:
        apagamento = st.selectbox("Apagamento (%)", options=[0, 1, 2,
