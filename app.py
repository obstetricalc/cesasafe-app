import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta

# ==========================================
# FUNDAÇÃO: CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CesaScore: Apoio à Decisão", 
    page_icon="🤰", 
    layout="wide"
)

# ==========================================
# INÍCIO DO APLICATIVO PRINCIPAL
# ==========================================
def main():
    # --- CABEÇALHO ---
    st.image("logo.png", width=500) 
    
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
    # --- FIM DO BLOCO 1 ---

    # ==========================================
    # BLOCO 2: HISTÓRICO OBSTÉTRICO
    # ==========================================
    st.header("2. Histórico Obstétrico")
    
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

    st.markdown("") 
    
    # --- Datação da Gestação (DUM) ---
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

    # --- Datação da Gestação (USG) ---
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

    st.markdown("")
    
    # --- Comorbidades e Fatores de Risco ---
    col_comorb, col_obst = st.columns(2)
    
    with col_comorb:
        st.markdown("**Comorbidades Maternas**")
        hipertensao = st.checkbox("Hipertensão Crônica")
        diabetes_previa = st.checkbox("Diabetes Pré-gestacional")
        obesidade = st.checkbox("Obesidade")
        cardiopatias = st.checkbox("Cardiopatias")
        doenca_renal = st.checkbox("Doença Renal Crônica")
        doenca_autoimune = st.checkbox("Doença Autoimune")
        outras_comorb = st.checkbox("Outras")
        
    with col_obst:
        st.markdown("**Fatores Obstétricos da Gestação Atual**")
        pre_eclampsia = st.checkbox("Pré-eclâmpsia")
        diabetes_gest = st.checkbox("Diabetes Gestacional")
        placenta_previa = st.checkbox("Placenta Prévia")
        gemelar = st.checkbox("Gestação Gemelar")
        ciur = st.checkbox("Restrição de Crescimento Fetal")
        macrossomia = st.checkbox("Macrossomia Fetal")
        oligodramnio = st.checkbox("Oligodrâmnio")
        polidramnio = st.checkbox("Polidrâmnio")
        apres_pelvica = st.checkbox("Apresentação Pélvica")
        apres_transversa = st.checkbox("Apresentação Transversa")

    st.markdown("---")
    # --- FIM DO BLOCO 2 ---

    # ==========================================
    # BLOCO 3: EXAME FÍSICO E OBSTÉTRICO
    # ==========================================
    st.header("3. Exame Físico e Obstétrico")
    
    # --- Avaliação Fetal e Dinâmica Uterina ---
    st.subheader("Avaliação Fetal e Dinâmica Uterina")
    col_fetos, col_apres, col_tp, col_ig_rob = st.columns(4)
    
    with col_fetos:
        tipo_gestacao = st.selectbox("Número de Fetos", ["Único", "Múltiplo (Gêmeos ou mais)"])
    
    with col_apres:
        apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Situação Transversa/Oblíqua"])
    
    with col_tp:
        inicio_tp = st.selectbox("Início do Trabalho de Parto", ["Espontâneo", "Induzido", "Cesárea antes do TP"])
        
    with col_ig_rob:
        ig_termo = st.selectbox("Classificação da IG", ["≥ 37 semanas (Termo)", "< 37 semanas (Pré-termo)"])

    col_au, col_bcf, col_vazia1, col_vazia2 = st.columns(4)
    with col_au:
        au = st.number_input("AU - Altura Uterina (cm)", min_value=0, max_value=60, value=0, step=1)
    with col_bcf:
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, step=1, help="Faixa de normalidade considerada: 120 a 160 bpm")

    st.markdown("")

    # --- Toque Vaginal (Avaliação do Colo Uterino) ---
    st.subheader("Toque Vaginal")
    st.markdown("Preencha os dados do exame de toque para avaliação da maturidade cervical e progressão.")
    
    col_dilat, col_esvaec, col_altura = st.columns(3)
    with col_dilat:
        dilatacao = st.selectbox("Dilatação (cm)", ["Fechado (0 cm)", "1 a 2 cm", "3 a 4 cm", "5 cm ou mais"])
    with col_esvaec:
        esvaecimento = st.selectbox("Esvaecimento (%)", ["0 a 30%", "40 a 50%", "60 a 70%", "80% ou mais"])
    with col_altura:
        altura_apres = st.selectbox("Altura da Apresentação (De Lee)", ["-3", "-2", "-1 ou 0", "+1 ou +2"])

    col_consist, col_posic, col_vazia3 = st.columns(3)
    with col_consist:
        consistencia = st.selectbox("Consistência do Colo", ["Firme", "Médio", "Amolecido"])
    with col_posic:
        posicao_colo = st.selectbox("Posição do Colo", ["Posterior", "Centralizado", "Anterior"])

    st.markdown("---")
    # --- FIM DO BLOCO 3 ---

# ==========================================
# COMANDO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()
