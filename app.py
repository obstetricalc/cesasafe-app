# ==========================================
# FUNDAÇÃO: IMPORTAÇÕES E CONFIGURAÇÃO
# (Cole este bloco no topo absoluto do seu documento)
# ==========================================
import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta

# Configuração da aba do navegador e layout
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
    
    # Criamos duas colunas para organizar os campos lado a lado
    c_ident1, c_ident2 = st.columns([2, 1])
    
    with c_ident1:
        # st.text_input recebe o nome da paciente digitado livremente
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c_ident2:
        # st.number_input recebe a idade (este valor será vital para o modelo preditivo MFMU depois)
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=None, step=1, placeholder="Ex: 30")

    st.markdown("---")
    # --- FIM DO BLOCO 1 ---

# ==========================================
# COMANDO DE EXECUÇÃO
# (Esta parte rodará o aplicativo. Deixe-a sempre no final do documento)
# ==========================================
if __name__ == "__main__":
    main()
