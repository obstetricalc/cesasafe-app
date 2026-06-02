import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta

# ==========================================
# FUNDAÇÃO: CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CesaSafe: Apoio à Decisão", 
    page_icon="🤰", 
    layout="wide"
)

# ==========================================
# INÍCIO DO APLICATIVO PRINCIPAL
# ==========================================
def main():
    # --- CABEÇALHO ---
    st.title("🤰 CesaSafe: Sistema de Apoio à Decisão Obstétrica")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais. 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    st.markdown("---")

    # ==========================================
    # BLOCO 1: IDENTIFICAÇÃO
    # ==========================================
    st.header("1. Identificação")
    
    hoje = date.today()
    data_minima = date(hoje.year - 60, 1, 1)
    data_maxima = hoje
    
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c2:
        data_nasc = st.date_input("Data de Nascimento", value=None, min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        
    with c3:
        idade = None
        if data_nasc:
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.metric("Idade", f"{idade} anos")

    c4, c5, c6 = st.columns(3)
    
    with c4:
        peso_kg = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 70.5")
        
    with c5:
        altura_m = st.number_input("Altura (metros)", min_value=1.00, max_value=2.50, value=None, step=0.01, format="%.2f", placeholder="Ex: 1.60")
        
    with c6:
        imc = None
        if peso_kg is not None and altura_m is not None and altura_m > 0:
            imc = peso_kg / (altura_m ** 2)
            st.metric("IMC", f"{imc:.1f} kg/m²")

    st.markdown("---")

    # ==========================================
    # BLOCO 2: HISTÓRICO OBSTÉTRICO E RISCOS
    # ==========================================
    st.header("2. Histórico Obstétrico e Fatores de Risco")
    
    # --- Gestas e Paridade ---
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1, step=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0, step=1)
    with col_pc:
        partos_cesareos = st.number_input("PC (Partos Cesáreos)", min_value=0, value=0, step=1)
    with col_a:
        abortos = st.number_input("A (Abortos)", min_value=0, value=0, step=1)

    # --- Alerta Interativo de Parto Cesáreo Anterior ---
    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com histórico de Parto Cesáreo Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo ocorreu o último parto cesáreo?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("---") 
    
    # --- Comorbidades e Fatores de Risco ---
    st.subheader("Avaliação de Riscos")
    col_comorb, col_obst = st.columns(2)
    
    with col_comorb:
        st.markdown("**Comorbidades (Pré-existentes)**")
        hipertensao = st.checkbox("Hipertensão Crônica Tratada")
        diabetes_previa = st.checkbox("Diabetes Mellitus Prévia")
        cardiopatia = st.checkbox("Cardiopatia Grave")
        
    with col_obst:
        st.markdown("**Fatores de Risco Obstétrico**")
        diabetes_gest = st.checkbox("Diabetes Gestacional")
        pre_eclampsia = st.checkbox("Pré-eclâmpsia / Eclâmpsia")
        
        outros_fatores = st.multiselect(
            "Outras Intercorrências na Gestação:",
            ["Nenhum", 
             "Placenta Prévia Total", 
             "Herpes Genital Ativo", 
             "HIV (Carga Viral >1000 ou Desconhecida)", 
             "Desproporção Cefalopélvica (DCP)", 
             "Rotura Uterina Prévia",
             "Parto Prematuro Anterior"]
        )

    st.markdown("---")
    
    # --- Datação da Gestação (DUM e USG) ---
    st.subheader("Datação da Gestação")
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    with col_dum:
        dum = st.date_input("DUM (Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    with col_ig_dum:
        if dum:
            dias_gest = (hoje - dum).days 
            if dias_gest < 0: dias_gest = 0
            ig_sem = dias_gest // 7
            ig_dias = dias_gest % 7
            st.metric("IG (pela DUM)", f"{ig_sem} sem e {ig_dias} dias")
            
    with col_dpp_dum:
        if dum:
            dpp_calc = dum + timedelta(days=280)
            st.metric("DPP (pela DUM)", dpp_calc.strftime('%d/%m/%Y'))

    col_eco, col_ig_eco, col_vazia = st.columns(3)
    
    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (Eco)", value=None, format="DD/MM/YYYY")
    
    with col_ig_eco:
        if dpp_eco:
            dt_concepcao_eco = dpp_eco - timedelta(days=280)
            dias_gest_eco = (hoje - dt_concepcao_eco).days
            if dias_gest_eco < 0: dias_gest_eco = 0
            ig_sem_eco = dias_gest_eco // 7
            ig_dias_eco = dias_gest_eco % 7
            st.metric("IG (pela USG)", f"{ig_sem_eco} sem e {ig_dias_eco} dias")

    st.markdown("---")

    # ==========================================
    # BLOCO 3: AVALIAÇÃO FETAL E CLASSIFICAÇÃO DE ROBSON
    # ==========================================
    st.header("3. Avaliação Fetal e Classificação de Robson")
    
    st.markdown("O sistema cruza as informações fetais e de trabalho de parto com o Histórico Obstétrico (G/P/C) para calcular o Grupo de Robson automaticamente.")
    
    # --- Linha 1: Variáveis para Robson ---
    col_fetos, col_apres, col_tp, col_ig_rob = st.columns(4)
    
    with col_fetos:
        tipo_gestacao = st.selectbox("Número de Fetos", ["Único", "Múltiplo (Gêmeos ou mais)"])
    
    with col_apres:
        apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Situação Transversa/Oblíqua"])
    
    with col_tp:
        inicio_tp = st.selectbox("Início do Trabalho de Parto", ["Espontâneo", "Induzido", "Cesárea antes do TP"])
        
    with col_ig_rob:
        ig_termo = st.selectbox("Idade Gestacional", ["≥ 37 semanas (Termo)", "< 37 semanas (Pré-termo)"])

    # --- Linha 2: Exame Físico Básico ---
    col_au, col_bcf, col_vazia1, col_vazia2 = st.columns(4)
    with col_au:
        au = st.number_input("AU - Altura Uterina (cm)", min_value=0, max_value=60, value=0, step=1)
    with col_bcf:
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, step=1, help="Faixa de normalidade considerada: 120 a 160 bpm")

    # ==========================================
    # ALGORITMO AUTOMÁTICO DE ROBSON
    # ==========================================
    paridade_total = partos_normais + partos_cesareos
    nulipara = (paridade_total == 0)
    multipara = (paridade_total > 0)
    tem_cesarea_previa = (partos_cesareos > 0)
    
    grupo_robson = "Indefinido"
    descricao_robson = ""

    if tipo_gestacao == "Múltiplo (Gêmeos ou mais)":
        grupo_robson = "Grupo 8"
        descricao_robson = "Todas as gestações múltiplas (incluindo parto cesáreo prévio)."
    elif apresentacao == "Situação Transversa/Oblíqua":
        grupo_robson = "Grupo 9"
        descricao_robson = "Todas as gestantes com feto único em situação transversa ou oblíqua."
    elif apresentacao == "Pélvica":
        if nulipara:
            grupo_robson = "Grupo 6"
            descricao_robson = "Nulíparas, feto único, apresentação pélvica."
        else:
            grupo_robson = "Grupo 7"
            descricao_robson = "Multíparas, feto único, apresentação pélvica, com ou sem parto cesáreo anterior."
    elif ig_termo == "< 37 semanas (Pré-termo)":
        grupo_robson = "Grupo 10"
        descricao_robson = "Todas as gestantes com feto único, apresentação cefálica, pré-termo (< 37 semanas)."
    else:
        if nulipara:
            if inicio_tp == "Espontâneo":
                grupo_robson = "Grupo 1"
                descricao_robson = "Nulíparas, feto único, cefálico, ≥ 37 semanas, TP espontâneo."
            else:
                grupo_robson = "Grupo 2"
                descricao_robson = "Nulíparas, feto único, cefálico, ≥ 37 semanas, induzido ou cesárea antes do TP."
        elif multipara:
            if tem_cesarea_previa:
                grupo_robson = "Grupo 5"
                descricao_robson = "Multíparas, feto único, cefálico, ≥ 37 semanas, com 1 ou mais partos cesáreos anteriores."
            else:
                if inicio_tp == "Espontâneo":
                    grupo_robson = "Grupo 3"
                    descricao_robson = "Multíparas (sem parto cesáreo anterior), feto único, cefálico, ≥ 37 semanas, TP espontâneo."
                else:
                    grupo_robson = "Grupo 4"
                    descricao_robson = "Multíparas (sem parto cesáreo anterior), feto único, cefálico, ≥ 37 semanas, induzido ou cesárea antes do TP."

    st.markdown("")
    st.success(f"📊 **Classificação: {grupo_robson}** \n*{descricao_robson}*")

    st.markdown("---")

# ==========================================
# COMANDO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()
