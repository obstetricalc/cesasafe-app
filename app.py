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

    # --- 1. DADOS DA GESTANTE ---
    st.header("1. Dados Clínicos e Obstétricos")
    
    # Identificação Básica
    c_dados1, c_dados2 = st.columns([2, 1])
    with c_dados1:
        nome = st.text_input("Nome da Paciente")
    with c_dados2:
        idade = st.number_input("Idade", min_value=10, max_value=60, value=25)

    # Histórico Obstétrico (G P A)
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

    # Alerta de Cesárea Prévia
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo foi a última cesárea?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )
    
    st.markdown("---")
    
    # Cálculo de IG e DPP
    st.subheader("Cálculo da Idade Gestacional (IG)")
    
    tipo_calculo = st.radio("Método de Datação:", ("Pela DUM", "Pela USG (DPP Eco)"), horizontal=True)
    
    ig_semanas = 0 # Variável inicial
    ig_dias = 0    # Variável inicial
    
    col_data1, col_data2 = st.columns(2)
    
    if tipo_calculo == "Pela DUM":
        with col_data1:
            dum = st.date_input("Data da Última Menstruação (DUM)", value=date.today() - timedelta(days=280))
        
        # Cálculos DUM
        dias_gestacao = (date.today() - dum).days
        ig_semanas = dias_gestacao // 7
        ig_dias = dias_gestacao % 7
        dpp_calc = dum + timedelta(days=280)
        
        with col_data2:
            st.metric("IG (DUM)", f"{ig_semanas}s e {ig_dias}d")
            st.metric("DPP (Provável)", dpp_calc.strftime('%d/%m/%Y'))
            
    else: # Pela USG
        with col_data1:
            dpp_eco = st.date_input("DPP da 1ª USG (Data Provável do Parto)")
            
        # Cálculos USG (Retroativo)
        # Se a DPP é X, a concepção foi X - 280. A IG é Hoje - Concepção.
        data_concepcao_teorica = dpp_eco - timedelta(days=280)
        dias_gestacao_usg = (date.today() - data_concepcao_teorica).days
        
        ig_semanas = dias_gestacao_usg // 7
        ig_dias = dias_gestacao_usg % 7
        
        with col_data2:
            st.metric("IG (USG)", f"{ig_semanas}s e {ig_dias}d")
            st.caption("Cálculo baseado na DPP informada.")

    st.markdown("---")

    # --- 2. ÍNDICE DE BISHOP (Maturação Cervical) ---
    st.header("2. Índice de Bishop")
    st.caption("Avaliação para sucesso de indução vs. Cesárea")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        dilatacao = st.selectbox("Dilatação (cm)", options=[0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥ 5 cm (3)"][x])
    with c2:
        apagamento = st.selectbox("Apagamento (%)", options=[0, 1, 2, 3], format_func=lambda x: ["0-30% (0)", "40-50% (1)", "60-70% (2)", "≥ 80% (3)"][x])
    with c3:
        altura = st.selectbox("Altura (De Lee)", options=[0, 1, 2, 3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1 ou 0 (2)", "+1 ou +2 (3)"][x])
    with c4:
        consistencia = st.selectbox("Consistência", options=[0, 1, 2], format_func=lambda x: ["Firme (0)", "Média (1)", "Amolecida (2)"][x])
    with c5:
        posicao = st.selectbox("Posição", options=[0, 1, 2], format_func=lambda x: ["Posterior (0)", "Média (1)", "Anterior (2)"][x])

    score_bishop = dilatacao + apagamento + altura + consistencia + posicao
    st.metric("Score de Bishop Total", f"{score_bishop}/13")

    # --- 3. ESCORE DE MALINAS (Risco de Parto Iminente) ---
    st.header("3. Escore de Malinas")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        m_paridade = st.selectbox("Paridade (Malinas)", [0, 1, 2], format_func=lambda x: ["1 parto (0)", "2 partos (1)", "≥3 partos (2)"][x])
        m_duracao = st.selectbox("Duração Trabalho de Parto", [0, 1, 2], format_func=lambda x: ["< 3h (0)", "3-5h (1)", "> 6h (2)"][x])
    with m2:
        m_membrana = st.selectbox("Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras (0)", "Rotas recent. (1)", "Rotas >1h (2)"][x])
        m_distancia = st.selectbox("Dilatação/Descida", [0, 1, 2], format_func=lambda x: ["Alta/Fechada (0)", "Média (1)", "Baixa/Completa (2)"][x])
    with m3:
        score_malinas = m_paridade + m_duracao + m_membrana + m_distancia
        st.metric("Score de Malinas", score_malinas)
        if score_malinas < 5:
            st.success("Malinas: Transporte seguro (Parto não iminente)")
        elif score_malinas < 10:
            st.warning("Malinas: Atenção (Parto possível no transporte)")
        else:
            st.error("Malinas: Parto Iminente")

    st.markdown("---")

    # --- 4. CARDIOTOCOGRAFIA & INDICAÇÕES ---
    st.header("4. Avaliação Fetal e Indicações")
    col_fetal, col_indica = st.columns(2)

    with col_fetal:
        st.subheader("Cardiotocografia (CTG)")
        ctg_class = st.radio("Classificação NICHD", 
            ("Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"))
        liquido = st.selectbox("Líquido Amniótico", ["Claro", "Meconial Fluido", "Meconial Espesso"])

    with col_indica:
        st.subheader("Fatores de Risco / Indicações")
        indicacoes_abs = st.multiselect("Indicações Absolutas/Relativas", 
            ["Nenhuma", "Placenta Prévia Total", "Apresentação Pélvica/Córmica", 
             "Iteratividade (2+ cesáreas)", "Herpes Genital Ativo", 
             "Desproporção Cefalopélvica (DCP)", "Sofrimento Fetal Agudo", 
             "Preeclampsia Grave / Eclampsia", "HIV Carga Viral Desconhecida/>1000"])

    # --- 5. GERAÇÃO DO RELATÓRIO ---
    st.markdown("---")
    if st.button("GERAR RELATÓRIO FINAL", type="primary"):
        
        # Lógica de Sugestão
        sugestao = "Avaliar Individualmente"
        cor_box = "blue"
        
        if "Categoria III (Anormal)" in ctg_class or "Sofrimento Fetal Agudo" in indicacoes_abs:
            sugestao = "INDICAÇÃO DE CESÁREA DE EMERGÊNCIA (Sofrimento Fetal)"
            cor_box = "red"
        elif len([i for i in indicacoes_abs if i != "Nenhuma"]) > 0:
            sugestao = "INDICAÇÃO DE CESÁREA (Fatores Materno/Fetais)"
            cor_box = "orange"
        elif score_bishop < 6 and ig_semanas >= 41:
            sugestao = "Colo Desfavorável. Avaliar Maturação/Indução se houver indicação de interrupção."
            cor_box = "yellow"
        elif score_bishop >= 6:
            sugestao = "Favorável ao Parto Vaginal / Indução facilitada"
            cor_box = "green"

        # Exibição
        st.markdown(f"""
        ### 📄 Relatório de Admissão e Decisão Obstétrica
        **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        **Paciente:** {nome} | **Idade:** {idade} anos | **IG:** {ig_semanas}s {ig_dias}d
        **Histórico:** G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}
        
        ---
        #### 📊 Índices Calculados
        * **Bishop:** {score_bishop} ({'Desfavorável' if score_bishop < 6 else 'Favorável'})
        * **Malinas:** {score_malinas}
        
        #### 🩺 Vitalidade e Clínica
        * **CTG:** {ctg_class}
        * **Líquido:** {liquido}
        * **Fatores de Risco:** {', '.join(indicacoes_abs)}
        
        ---
        ### 🎯 Conclusão Sugerida
        """)
        
        if cor_box == "red":
            st.error(sugestao)
        elif cor_box == "orange":
            st.warning(sugestao)
        elif cor_box == "green":
            st.success(sugestao)
        else:
            st.info(sugestao)

        st.text_area("Conduta Médica (Preencher Manualmente)", height=100)
        st.caption("Imprima esta tela ou salve como PDF para anexar ao prontuário.")

if __name__ == "__main__":
    main()
