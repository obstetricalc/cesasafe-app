import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="ObstetriCalc: Apoio à Decisão", page_icon="👶", layout="wide")

def main():
    st.title("👶 ObstetriCalc: Relatório de Indicação de Via de Parto")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é auxiliar baseada em protocolos. A decisão clínica final é exclusiva do médico obstetra.
    """)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 1: DADOS CLÍNICOS E DATAÇÃO
    # ==========================================
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
    
    # Variáveis iniciais
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
        ig_dias = dias_gest % 7
        dpp_calc = dum + timedelta(days=280)
        dpp_str = dpp_calc.strftime('%d/%m/%Y')
        ig_str = f"{ig_sem}s e {ig_dias}d"

    with col_ig_dum:
        st.metric("IG (pela DUM)", ig_str)
    with col_dpp_dum:
        st.metric("DPP (Provável)", dpp_str)

    # LINHA B: DPPeco -> IGeco
    col_eco, col_ig_eco, col_vazio = st.columns(3)
    
    ig_sem_eco, ig_dias_eco = 0, 0
    ig_eco_str = "---"
    dpp_eco_str = "Não informada"

    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (DPP Eco)", value=None, format="DD/MM/YYYY")
    
    if dpp_eco:
        dpp_eco_str = dpp_eco.strftime('%d/%m/%Y')
        dt_concepcao_eco = dpp_eco - timedelta(days=280)
        dias_gest_eco = (date.today() - dt_concepcao_eco).days
        if dias_gest_eco < 0: dias_gest_eco = 0
        ig_sem_eco = dias_gest_eco // 7
        ig_dias_eco = dias_gest_eco % 7
        ig_eco_str = f"{ig_sem_eco}s e {ig_dias_eco}d"

    with col_ig_eco:
        st.metric("IG (pela USG)", ig_eco_str)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: AVALIAÇÃO FETAL (ATUALIZADA)
    # ==========================================
    st.header("2. Avaliação Fetal Física")
    
    col_au, col_bcf, col_sit, col_apres = st.columns(4)
    
    with col_au:
        au = st.number_input("AU - Altura Uterina (cm)", min_value=0, max_value=60, value=0)
    
    with col_bcf:
        # ATENÇÃO: Help atualizado para 120-160
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, help="Valor normal: 120 a 160 bpm")
    
    with col_sit:
        situacao = st.selectbox("Situação", ["Longitudinal", "Transversa", "Oblíqua"])
    
    with col_apres:
        apresentacao = st.selectbox("Apresentação", ["Cefálica", "Pélvica", "Córmica"])

    st.markdown("---")

    # ==========================================
    # SEÇÃO 3: BISHOP
    # ==========================================
    st.header("3. Índice de Bishop")
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

    # ==========================================
    # SEÇÃO 4: MALINAS
    # ==========================================
    st.header("4. Escore de Malinas")
    
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

    st.markdown("---")

    # ==========================================
    # SEÇÃO 5: CTG E RISCOS
    # ==========================================
    st.header("5. Avaliação Fetal e Indicações")
    col_fetal, col_indica = st.columns(2)

    with col_fetal:
        st.subheader("Cardiotocografia (CTG)")
        ctg_class = st.radio("Classificação NICHD", 
            ("Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"))
        liquido = st.selectbox("Líquido Amniótico", ["Claro", "Meconial Fluido", "Meconial Espesso"])

    with col_indica:
        st.subheader("Fatores de Risco / Indicações")
        indicacoes_abs = st.multiselect("Indicações Absolutas/Relativas", 
            ["Nenhuma", "Placenta Prévia Total", 
             "Iteratividade (2+ cesáreas)", "Herpes Genital Ativo", 
             "Desproporção Cefalopélvica (DCP)", "Sofrimento Fetal Agudo", 
             "Preeclampsia Grave / Eclampsia", "HIV Carga Viral Desconhecida/>1000"])

    # ==========================================
    # RELATÓRIO FINAL
    # ==========================================
    st.markdown("---")
    if st.button("GERAR RELATÓRIO FINAL", type="primary"):
        
        analise_texto = []
        
        # --- Lógica de Análise Fetal (ATUALIZADO 120-160) ---
        if bcf < 120:
            analise_texto.append(f"⚠️ **Bradicardia Fetal ({bcf} bpm):** Abaixo de 120 bpm. Necessária avaliação imediata da vitalidade fetal.")
        elif bcf > 160:
            analise_texto.append(f"⚠️ **Taquicardia Fetal ({bcf} bpm):** Acima de 160 bpm. Investigar corioamnionite, febre materna ou hipóxia inicial.")
        
        if apresentacao != "Cefálica":
            analise_texto.append(f"⚠️ **Apresentação {apresentacao}:** Risco para parto vaginal. Avaliar via de parto conforme protocolo (Cesárea ou Versão Externa).")

        # --- Lógica Bishop ---
        if score_bishop < 6:
            analise_texto.append(f"🔴 **Colo Desfavorável (Bishop {score_bishop}):** Colo imaturo. Caso haja indicação de interrupção, recomenda-se preparo cervical prévio.")
        else:
            analise_texto.append(f"🟢 **Colo Favorável (Bishop {score_bishop}):** Colo maduro. Indução facilitada.")

        # --- Lógica Malinas ---
        if score_malinas >= 10:
            analise_texto.append("🔴 **ALERTA DE PARTO IMINENTE (Malinas ≥ 10):** Não transportar. Preparar parto in loco.")
        elif score_malinas >= 5:
             analise_texto.append("🟡 **Malinas Intermediário:** Risco moderado no transporte.")

        # --- Lógica Vitalidade/Risco ---
        if "Categoria III (Anormal)" in ctg_class or "Sofrimento Fetal Agudo" in indicacoes_abs:
            analise_texto.append("🚨 **EMERGÊNCIA OBSTÉTRICA:** Sinais de sofrimento fetal. Extração imediata indicada.")
        
        if liquido == "Meconial Espesso":
            analise_texto.append("⚠️ **Mecônio Espesso:** Alerta para Síndrome de Aspiração Meconial.")

        # --- Lógica Cesárea Prévia ---
        if partos_cesareos > 0:
            if tempo_cesarea == "Menos de 2 anos (< 24 meses)":
                analise_texto.append("⚠️ **Iteratividade/Intervalo Curto:** Risco aumentado de rotura uterina.")
            else:
                analise_texto.append("ℹ️ **Cesárea Anterior:** Avaliar prova de trabalho de parto (TOLAC).")

        parecer_final = "\n\n".join(analise_texto)

        # Definição de Cor
        cor_box = "blue"
        if "EMERGÊNCIA" in parecer_final or "ALERTA" in parecer_final:
            cor_box = "red"
        elif "⚠️" in parecer_final or "🟡" in parecer_final:
            cor_box = "orange"
        else:
            cor_box = "green"

        # Exibição
        st.markdown(f"""
        ### 🏥 Parecer Clínico Automatizado
        **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        **Paciente:** {nome} ({idade} anos) | **G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}**
        """)
        
        if cor_box == "red": st.error(parecer_final)
        elif cor_box == "orange": st.warning(parecer_final)
        elif cor_box == "green": st.success(parecer_final)
        else: st.info(parecer_final)

        st.markdown("#### 📝 Detalhamento Clínico")
        
        # Resumo das datas
        txt_dum = f"{dum_str} (IG: {ig_str})" if dum else "Não informada"
        txt_usg = f"{dpp_eco_str} (IG: {ig_eco_str})" if dpp_eco else "Não informada"

        st.markdown(f"""
        * **Datação:** DUM: {txt_dum} | USG: {txt_usg}
        * **Exame Fetal:** AU: {au}cm | BCF: {bcf}bpm | Sit: {situacao} | Apres: {apresentacao}
        * **Colo (Bishop):** {score_bishop} | **Malinas:** {score_malinas}
        * **Vitalidade:** {ctg_class} | Líquido: {liquido}
        * **Fatores:** {', '.join(indicacoes_abs) if indicacoes_abs else 'Nenhum'}
        """)

        st.text_area("Conduta Médica e Prescrição", height=150)
        st.caption("CesaSafe App - Documento Auxiliar")

if __name__ == "__main__":
    main()
