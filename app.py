Fica muito mais elegante assim! Uma tela mais limpa, mostrando apenas as informações relevantes no momento certo, ajuda muito a evitar a poluição visual durante o plantão.

Para fazer isso no Streamlit, basta removermos a regra `else` (senão) que exibia os traços `"---"`. Assim, o código entende que se o campo estiver vazio, ele não deve desenhar absolutamente nada naquela coluna. Também alterei o nome para apenas "IMC", como você pediu.

Aqui está o código ajustado. Copie e cole por cima do seu arquivo atual para testar a mágica de aparecer e desaparecer:

```python
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
    
    # Pegamos a data atual do sistema para basear nossos cálculos
    hoje = date.today()
    # Criamos o limite mínimo (60 anos para trás a partir do dia 1º de janeiro) e máximo (hoje)
    data_minima = date(hoje.year - 60, 1, 1)
    data_maxima = hoje
    
    # --- Primeira Linha: Dados Pessoais ---
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c2:
        data_nasc = st.date_input("Data de Nascimento", value=None, min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        
    with c3:
        idade = None
        # A idade só vai aparecer na tela SE a data de nascimento for preenchida
        if data_nasc:
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.metric("Idade", f"{idade} anos")

    # --- Segunda Linha: Antropometria ---
    c4, c5, c6 = st.columns(3)
    
    with c4:
        peso_kg = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 70.5")
        
    with c5:
        altura_m = st.number_input("Altura (metros)", min_value=1.00, max_value=2.50, value=None, step=0.01, format="%.2f", placeholder="Ex: 1.60")
        
    with c6:
        imc = None
        # O IMC só vai aparecer na tela SE o peso e a altura forem preenchidos corretamente
        if peso_kg is not None and altura_m is not None and altura_m > 0:
            imc = peso_kg / (altura_m ** 2)
            st.metric("IMC", f"{imc:.1f} kg/m²")

    st.markdown("---")
    # --- FIM DO BLOCO 1 ---

# ==========================================
# COMANDO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()

```
