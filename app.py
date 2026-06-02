import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta

# ==========================================
# FUNÇÃO DE CÁLCULO VBAC (Nova Versão IMC)
# ==========================================
def calcular_vbac(idade, peso_kg, altura_cm, hipertensao=False, 
                  parada_progressao=False, parto_vaginal_previo=False, vbac_previo=False):
    """
    Calculadora de Probabilidade de Sucesso do VBAC
    Baseada no modelo MFMU / Grobman 2021
    """
    # 1. Converter altura para metros
    altura_m = altura_cm / 100

    # 2. Calcular IMC
    imc = peso_kg / (altura_m ** 2)

    # 3. Converter variáveis booleanas
    hipertensao = int(hipertensao)
    parada_progressao = int(parada_progressao)
    parto_vaginal_previo = int(parto_vaginal_previo)
    vbac_previo = int(vbac_previo)

    # 4. Calcular escore linear (x)
    x = (
        3.302
        - (0.043 * idade)
        - (0.052 * imc)
        + (0.832 * parto_vaginal_previo)
        + (0.489 * vbac_previo)
        - (0.622 * parada_progressao)
        - (0.513 * hipertensao)
    )

    # 5. Aplicar função logística
    probabilidade = 1 / (1 + math.exp(-x))

    # 6. Converter para percentual
    percentual = probabilidade * 100

    # 7. Classificação opcional
    if percentual < 40:
        classificacao = "Baixa probabilidade"
    elif percentual < 60:
        classificacao = "Probabilidade intermediária"
    elif percentual < 80:
        classificacao = "Boa probabilidade"
    else:
        classificacao = "Alta probabilidade"

    # 8. Retorno
    return {
        "IMC": round(imc, 2),
        "Probabilidade_VBAC": round(percentual, 2),
        "Classificacao": classificacao
    }

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CesaSafe: Apoio à Decisão", 
    page_icon="🤰", 
    layout="wide"
)

def main():
    # --- CABEÇALHO ---
    st.title("🤰 CesaSafe: Sistema de Apoio à Decisão Obstétrica")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais. 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    st.markdown("---")

    # ==========================================
    # SEÇÃO 1: IDENTIFICAÇÃO
    # ==========================================
    st.header("1. Identificação")
    
    c_ident1, c_ident2 = st.columns([2, 1])
    with c_ident1:
        nome = st.text_input("Nome da Paciente")
    with c_ident2:
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=None, step=1, placeholder="Digite a idade")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: HISTÓRICO OBSTÉTRICO E DATAÇÃO
    # ==========================================
    st.header("2. Histórico Obstétrico")
    
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value
