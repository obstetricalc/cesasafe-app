import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="ObstetriCalc: Apoio à Decisão", page_icon="👶", layout="wide")

def main():
    st.title("👶 ObstetriCalc: Relatório de Indicação de Via de Parto")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é auxiliar baseada em protocolos (ACOG/MS). A decisão clínica final é exclusiva do médico obstetra.
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
    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo foi a última cesárea?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("---")
    
    # --- DATAÇÃO ---
    st.subheader("📅 Datação da Gestação")

    # LINHA A: DUM -> IG -> DPP
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    # Variáveis iniciais (caso não preencha)
    ig_sem, ig_dias = 0, 0
    dpp_str = "---"
    ig_str = "---"
    dum_str = "Não informada"

    with col_dum:
        dum = st.date_input("DUM (Data Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    if dum:
        dum_str = dum.strftime('%d/%m/%Y')
        dias_gest = (date.today() - dum).days
        if dias_gest < 0: dias_gest = 0
        ig_sem = dias_gest // 7
        ig_dias =
