import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

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
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais (ACOG/MS). 
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
        # value=None deixa o campo vazio inicialmente
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=None, step=1, placeholder="Digite a idade")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: HISTÓRICO OBSTÉTRICO E DATAÇÃO
    # ==========================================
    st.header("2. Histórico Obstétrico")
    
    # --- G P C A ---
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0)
    with col_pc:
        # Rótulo alterado conforme solicitado
        partos_cesareos = st.number_input("PC (Partos Cesáreos)", min_value=0, value=0)
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

    st.markdown("") # Espaçamento visual
    
    # --- CÁLCULO DUM ---
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
        st.metric("IG (pela DUM)", ig_str)
    with col_dpp_dum:
        # Rótulo alterado conforme solicitado
        st.metric("DPP (pela DUM)", dpp_str)

    # --- CÁLCULO USG ---
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
    # SEÇÃO 3: AVALIAÇÃO FETAL
    # ==========================================
    st.header("3. Avaliação Fetal Física")
    
    col_au, col_bcf, col_sit, col_apres = st.columns(4)
    
    with col_au:
        au = st.number_input("AU - Altura Uterina (cm)", min_value=0, max_value=60, value=0)
    
    with col_bcf:
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, help="Faixa de normalidade considerada: 120 a 160 bpm")
    
    with col_sit:
        situacao = st.selectbox("Situação Fetal", ["Longitudinal", "Transversa", "Oblíqua"])
    
    with col_apres:
        apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Córmica"])

    st.markdown("---")

    # ==========================================
    # SEÇÃO 4: BISHOP
    # ==========================================
    st.header("4. Índice de Bishop")
    st.caption("Avaliação do colo uterino para predição de sucesso na indução do parto vaginal.")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        dilatacao = st.selectbox("Dilatação (cm)", options=[0, 1, 2, 3], format_func=lambda x: ["0 cm (0 pts)", "1-2 cm (1 pt)", "3-4 cm (2 pts)", "≥ 5 cm (3 pts)"][x])
    with c2:
        apagamento = st.selectbox("Apagamento (%)", options=[0, 1, 2, 3], format_func=lambda x: ["0-30% (0 pts)", "40-50% (1 pt)", "60-70% (2 pts)", "≥ 80% (3 pts)"][x])
    with c3:
        altura = st.selectbox("Altura (De Lee)", options=[0, 1, 2, 3], format_func=lambda x: ["-3 (0 pts)", "-2 (1 pt)", "-1 ou 0 (2 pts)", "+1 ou +2 (3 pts)"][x])
    with c4:
        consistencia = st.selectbox("Consistência", options=[0, 1, 2], format_func=lambda x: ["Firme (0 pts)", "Média (1 pt)", "Amolecida (2 pts)"][x])
    with c5:
        posicao = st.selectbox("Posição", options=[0, 1, 2], format_func=lambda x: ["Posterior (0 pts)", "Média (1 pt)", "Anterior (2 pts)"][x])

    score_bishop = dilatacao + apagamento + altura + consistencia + posicao
    st.metric("Score de Bishop Total", f"{score_bishop}/13 pontos")

    # ==========================================
    # SEÇÃO 5: MALINAS
    # ==========================================
    st.header("5. Escore de Malinas")
    st.caption("Avaliação de risco para parto iminente (transporte).")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        m_paridade = st.selectbox("Paridade (Malinas)", [0, 1, 2], format_func=lambda x: ["1 parto (0)", "2 partos (1)", "≥3 partos (2)"][x])
        m_duracao = st.selectbox("Duração do Trabalho de Parto", [0, 1, 2], format_func=lambda x: ["< 3h (0)", "3-5h (1)", "> 6h (2)"][x])
    with m2:
        m_membrana = st.selectbox("Integridade das Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras (0)", "Rotas recentes <1h (1)", "Rotas >1h (2)"][x])
        m_distancia = st.selectbox("Dilatação/Descida", [0, 1, 2], format_func=lambda x: ["Alta/Fechada (0)", "Média (1)", "Baixa/Completa (2)"][x])
    with m3:
        score_malinas = m_paridade + m_duracao + m_membrana + m_distancia
        st.metric("Score de Malinas", score_malinas)

    st.markdown("---")

    # ==========================================
    # SEÇÃO 6: CTG E RISCOS
    # ==========================================
    st.header("6. Avaliação Fetal e Fatores de Risco")
    col_fetal, col_indica = st.columns(2)

    with col_fetal:
        st.subheader("Cardiotocografia (CTG)")
        ctg_class = st.radio("Classificação NICHD", 
            ("Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"))
        liquido = st.selectbox("Aspecto do Líquido Amniótico", ["Claro / Grumos Finos", "Meconial Fluido", "Meconial Espesso"])

    with col_indica:
        st.subheader("Fatores de Risco / Indicações")
        indicacoes_abs = st.multiselect("Selecione os Fatores Presentes:", 
            ["Nenhum", "Placenta Prévia Total", 
             "Iteratividade (2+ cesáreas)", "Herpes Genital Ativo", 
             "Desproporção Cefalopélvica (DCP)", "Sofrimento Fetal Agudo", 
             "Pré-eclâmpsia Grave / Eclâmpsia", "HIV Carga Viral Desconhecida/>1000"])

    # ==========================================
    # RELATÓRIO FINAL
    # ==========================================
    st.markdown("---")
    if st.button("GERAR RELATÓRIO FINAL", type="primary"):
        
        analise_texto = []

        # --- LÓGICA IDADE MATERNA ---
        # Verifica se a idade foi preenchida (não é None)
        if idade is not None:
            if idade < 16:
                analise_texto.append(f"⚠️ **Idade Materna ({idade} anos):** Adolescência precoce. Risco biológico aumentado para Desproporção Cefalopélvica (DCP) por imaturidade pélvica, além de risco para síndromes hipertensivas.")
            elif idade < 20:
                analise_texto.append(f"ℹ️ **Idade Materna ({idade} anos):** Gravidez na adolescência. Monitorar riscos de síndromes hipertensivas e prematuridade.")
            elif idade >= 40:
                analise_texto.append(f"⚠️ **Idade Materna Avançada ({idade} anos):** Alto risco para comorbidades (HAS, Diabetes), placentação anômala e óbito fetal. Vigilância rigorosa.")
            elif idade >= 35:
                analise_texto.append(f"ℹ️ **Idade Materna ({idade} anos):** Idade avançada. Risco aumentado para diabetes gestacional e hipertensão.")
        else:
            analise_texto.append("⚠️ **Idade Materna:** Não informada. Recomenda-se preencher para melhor avaliação de riscos.")

        # --- Lógica de Análise Fetal (BCF 120-160) ---
        if bcf < 120:
            analise_texto.append(f"⚠️ **Bradicardia Fetal ({bcf} bpm):** Frequência cardíaca basal abaixo de 120 bpm. Necessária avaliação imediata da vitalidade fetal para descartar sofrimento agudo.")
        elif bcf > 160:
            analise_texto.append(f"⚠️ **Taquicardia Fetal ({bcf} bpm):** Frequência cardíaca basal acima de 160 bpm. Investigar causas como corioamnionite, febre materna ou hipóxia fetal inicial.")
        
        if apresentacao != "Cefálica":
            analise_texto.append(f"⚠️ **Apresentação {apresentacao}:** Fator de risco para parto vaginal. Avaliar via de parto conforme protocolo institucional (Cesárea ou Versão Cefálica Externa se aplicável).")

        # --- Lógica Bishop ---
        if score_bishop < 6:
            analise_texto.append(f"🔴 **Colo Desfavorável (Bishop {score_bishop}):** Colo imaturo. Se houver indicação clínica de interrupção da gestação, recomenda-se preparo cervical (maturação) prévio.")
        else:
            analise_texto.append(f"🟢 **Colo Favorável (Bishop {score_bishop}):** Colo maduro. Condições favoráveis à indução do parto vaginal.")

        # --- Lógica Malinas ---
        if score_malinas >= 10:
            analise_texto.append("🔴 **ALERTA DE PARTO IMINENTE (Malinas ≥ 10):** Alto risco de parto no transporte. Recomenda-se preparo para assistência ao parto in loco, a menos que o transporte seja imediato e curto.")
        elif score_malinas >= 5:
             analise_texto.append("🟡 **Malinas Intermediário:** Risco moderado de parto durante o transporte. Avaliar tempo de deslocamento.")

        # --- Lógica Vitalidade/Risco ---
        if "Categoria III (Anormal)" in ctg_class or "Sofrimento Fetal Agudo" in indicacoes_abs:
            analise_texto.append("🚨 **EMERGÊNCIA OBSTÉTRICA:** Sinais sugestivos de sofrimento fetal agudo. Indicação de extração fetal imediata (via mais rápida).")
        
        if liquido == "Meconial Espesso":
            analise_texto.append("⚠️ **Líquido Meconial Espesso:** Risco elevado de Síndrome de Aspiração Meconial (SAM). Necessária presença de equipe de neonatologia/pediatria na sala de parto.")

        # --- Lógica Cesárea Prévia ---
        if partos_cesareos > 0:
            if tempo_cesarea == "Menos de 2 anos (< 24 meses)":
                analise_texto.append("⚠️ **Cesárea Anterior (Iteratividade/Intervalo Curto):** Risco aumentado de rotura uterina em prova de trabalho de parto.")
            else:
                analise_texto.append("ℹ️ **Cesárea Anterior:** Paciente candidata à prova de trabalho de parto (TOLAC) se não houver contraindicações obstétricas recorrentes.")

        parecer_final = "\n\n".join(analise_texto)

        # Definição de Cor do Box
        cor_box = "blue"
        if "EMERGÊNCIA" in parecer_final or "ALERTA" in parecer_final:
            cor_box = "red"
        elif "⚠️" in parecer_final or "🟡" in parecer_final:
            cor_box = "orange"
        else:
            cor_box = "green"

        # Exibição do Relatório
        st.markdown(f"""
        ### 🏥 Parecer Clínico Automatizado - CesaSafe
        **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        **Identificação:** {nome if nome else 'Não identificada'} ({idade if idade else 'Idade não informada'} anos)
        **Obstetrícia:** G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}
        """)
        
        if cor_box == "red": st.error(parecer_final)
        elif cor_box == "orange": st.warning(parecer_final)
        elif cor_box == "green": st.success(parecer_final)
        else: st.info(parecer_final)

        st.markdown("#### 📝 Detalhamento dos Parâmetros")
        
        # Resumo das datas
        txt_dum = f"{dum_str} (IG: {ig_str})" if dum else "Não informada"
        txt_usg = f"{dpp_eco_str} (IG: {ig_eco_str})" if dpp_eco else "Não informada"

        st.markdown(f"""
        * **Datação:** DUM: {txt_dum} | USG: {txt_usg}
        * **Exame Fetal:** AU: {au}cm | BCF: {bcf}bpm | Sit: {situacao} | Apres: {apresentacao}
        * **Cérvice (Bishop):** {score_bishop} pts | **Risco Transporte (Malinas):** {score_malinas} pts
        * **Vitalidade:** {ctg_class} | Líquido: {liquido}
        * **Fatores de Risco:** {', '.join(indicacoes_abs) if indicacoes_abs else 'Nenhum'}
        """)

        st.text_area("Conduta Médica, Prescrição e Orientações", height=150, placeholder="Descreva aqui o plano terapêutico...")
        st.caption("CesaSafe App - Ferramenta de Apoio à Decisão Clínica | Mestrado CIPE/UEPA")

if __name__ == "__main__":
    main()
