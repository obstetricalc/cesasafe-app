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
    
    # --- Primeira Linha: Dados Pessoais ---
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c2:
        # st.date_input recebe a data. O format="DD/MM/YYYY" garante o padrão brasileiro.
        data_nasc = st.date_input("Data de Nascimento", value=None, format="DD/MM/YYYY")
        
    with c3:
        # Lógica para calcular a idade automaticamente
        idade = None
        if data_nasc:
            hoje = date.today()
            # Cálculo exato considerando se a paciente já fez aniversário no ano atual
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day)
