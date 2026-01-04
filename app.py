import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="CesaSafe: Apoio à Decisão", page_icon="🤰", layout="wide")

def main():
    st.title("🤰 CesaSafe: Sistema de Apoio à Decisão Obstétrica")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais (ACOG/MS). 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 1: DADOS CLÍNICOS E DATAÇÃO
    # ==========================================
    st.header("1. Identificação e Anamnese Obstétrica")
    
    # Linha 1: Nome e Idade
    c_dados1, c_dados2 = st.columns([2, 1])
    with c_dados1:
        nome = st.text_input("Nome da Paciente")
    with c_dados2:
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=25)

    # Linha 2: Histórico Obstétrico (G P A)
    st.markdown("**Histórico Obstétrico:**")
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G - Gestações", min_value=1, value=1)
    with col_pn:
        partos_normais = st.number_input("PN - Partos Vaginais", min_value=0, value=0)
    with col_pc:
        partos_cesareos = st.number_input("PC - Partos Cesáreos", min_value=0, value=0)
    with col_a:
        abortos = st.number_input("A - Abortos", min_value=0, value=0)

    # Alerta de Cesárea Prévia (Condicional)
    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio(
            "Intervalo Interpartal (Tempo desde a última cesárea):",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("---")
    
    # --- DATAÇÃO ---
    st.subheader("📅 Cronologia e Datação")

    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    # Variáveis iniciais
    ig_sem, ig_dias = 0, 0
    dpp_str = "---"
    ig_str = "---"
    dum_str = "Não informada"

    with col_dum:
        dum = st.date_input("DUM (Data da Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    if dum:
        dum_str = dum.strftime('%d/%m/%Y')
        dias_gest = (date.today() - dum).days
        if dias_gest < 0: dias_gest = 0
        ig_sem = dias_gest // 7
        ig_dias = dias_gest % 7
        dpp_calc = dum + timedelta(days=280)
        dpp_str = dpp_calc.strftime('%d/%m/%Y')
        ig_str = f"{ig_sem}s e {ig_dias}d"

    with col_ig_dum:
        st.metric("IG (Calculada pela DUM)", ig_str)
    with col_dpp_dum:
        st.metric("DPP (Provável)", dpp_str)

    # LINHA B: DPPeco -> IGeco
    col_eco, col_ig_eco, col_vazio = st.columns(3)
    
    ig_sem_eco, ig_dias_eco = 0, 0
    ig_eco_str = "---"
    dpp_eco_str = "Não informada"

    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (Data Provável ECO)", value=None, format="DD/MM/YYYY")
    
    if dpp_eco:
        dpp_eco_str = dpp_eco.strftime('%d/%m/%Y')
        dt_concepcao_eco = dpp_eco - timedelta(days=280)
        dias_gest_eco = (date.today() - dt_concepcao_eco).days
        if dias_gest_eco < 0: dias_gest_eco = 0
        ig_sem_eco = dias_gest_eco // 7
        ig_dias_eco = dias_gest_eco % 7
        ig_eco_str = f"{ig_sem_eco}s e {ig_dias_eco}d"

    with col_ig_eco:
        st.metric("IG (Calculada pela USG)", ig_eco_str)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: BIOMETRIA E ESTÁTICA
    # ==========================================
    st.header("2. Biometria e Estática Fetal")
    
    col_au, col_bcf, col_sit, col_apres = st.columns(4)
    
    with col_au:
        au = st.number_input("Altura Uterina - AU (cm)", min_value=0, max_value=60, value=0)
    
    with col_bcf:
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, help="Faixa de normalidade: 120 a 160 bpm")
    
    with col_sit:
        situacao = st.selectbox("Situação Fetal", ["Longitudinal", "Transversa", "Oblíqua"])
    
    with col_apres:
        apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Córmica"])

    st.markdown("---")

    # ==========================================
    # SEÇÃO 3: BISHOP
    # ==========================================
    st.header("3. Índice de Bishop (Maturação Cervical)")
    st.caption("Avaliação do colo uterino para predição de sucesso na indução do parto.")
    
    c1, c2
