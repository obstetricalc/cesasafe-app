import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="ObstetriCalc: Apoio à Decisão", page_icon="👶", layout="wide")

def main():
    st.title("👶 ObstetriCalc: Relatório de Indicação de Via de Parto")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é auxiliar baseada em protocolos (ACOG/MS). A decisão clínica final é exclusiva do médico obstetra.
    """)
    
    st.markdown("---")

    # --- 1. DADOS CLÍNICOS E DATAÇÃO ---
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
    
    # Variáveis iniciais (caso não preencha)
    ig_sem, ig_dias = 0, 0
    dpp_str = "---"
    ig_str = "---"
    dum_str = "Não informada"

    with col_dum:
        # value=None deixa vazio. format muda para Dia/Mês/Ano
        dum = st.date_input("DUM (Data Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    if dum:
        # Cálculo só acontece se DUM for preenchida
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
    
    # Variáveis iniciais USG
    ig_sem_eco, ig_dias_eco = 0, 0
    ig_eco_str = "---"
    dpp_eco_str = "Não informada"

    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (DPP Eco)", value=None, format="DD/MM/YYYY")
    
    if dpp_eco:
        # Cálculo só acontece se USG for preenchida
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

    # --- 2. ÍNDICE DE BISHOP ---
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

    # --- 3. ESCORE DE MALINAS ---
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

    st.markdown("---")

    # --- 4. CARDIOTOCOGRAFIA E INDICAÇÕES ---
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

    # --- 5. RELATÓRIO FINAL INTELIGENTE ---
    st.markdown("---")
    if st.button("GERAR RELATÓRIO FINAL", type="primary"):
        
        # --- LÓGICA DE INTELIGÊNCIA CLÍNICA ---
        analise_texto = []

        # 1. Análise Bishop
        if score_bishop < 6:
            analise_texto.append(f"🔴 **Colo Desfavorável (Bishop {score_bishop}):** Colo imaturo. Caso haja indicação de interrupção da gestação, recomenda-se **preparo cervical** (ex: Misoprostol ou cateter de Foley) antes da infusão de ocitocina, para reduzir risco de falha de indução.")
        else:
            analise_texto.append(f"🟢 **Colo Favorável (Bishop {score_bishop}):** Colo maduro. Alta probabilidade de sucesso em caso de indução com ocitocina ou amniotomia.")

        # 2. Análise Malinas (Transporte)
        if score_malinas < 5:
            analise_texto.append("🟢 **Malinas Baixo:** Baixo risco de parto iminente nas próximas horas. Transporte seguro para unidade de referência.")
        elif score_malinas < 10:
            analise_texto.append("🟡 **Malinas Intermediário:** Atenção. Risco moderado de parto no transporte. Avaliar distância da referência.")
        else:
            analise_texto.append("🔴 **ALERTA DE PARTO IMINENTE (Malinas ≥ 10):** Expulsivo provável em menos de 1 hora. Recomenda-se **NÃO TRANSPORTAR** e preparar material para parto no local, a menos que o transporte seja extremamente breve.")

        # 3. Análise Vitalidade/Risco
        if "Categoria III (Anormal)" in ctg_class or "Sofrimento Fetal Agudo" in indicacoes_abs:
            analise_texto.append("🚨 **EMERGÊNCIA OBSTÉTRICA:** Sinais de comprometimento fetal grave. Indicação de extração fetal imediata (Via mais rápida). Medidas de reanimação intrauterina indicadas enquanto se prepara o parto.")
        elif "Categoria II (Indeterminado)" in ctg_class:
            analise_texto.append("🟡 **Alerta Vitalidade:** CTG Indeterminada. Necessário vigilância contínua, avaliação de variabilidade e manobras de reanimação intrauterina. Se persistir, considerar parto.")
        
        if liquido == "Meconial Espesso":
            analise_texto.append("⚠️ **Mecônio Espesso:** Alerta para Síndrome de Aspiração Meconial. Presença de equipe de neonatologia essencial.")

        # 4. Análise Cesárea Prévia
        if partos_cesareos > 0:
            if tempo_cesarea == "Menos de 2 anos (< 24 meses)":
                analise_texto.append("⚠️ **Cesárea Anterior Recente (Interpartal Curto):** Risco aumentado de rotura uterina em caso de trabalho de parto. Monitorização rigorosa ou cesárea eletiva a depender da cicatriz.")
            else:
                analise_texto.append("ℹ️ **Cesárea Anterior:** Candidata à prova de trabalho de parto (TOLAC) se não houver outras contraindicações.")

        # Concatenação do texto
        parecer_final = "\n\n".join(analise_texto)

        # Definição de Cor do Box Principal
        cor_box = "blue"
        if "EMERGÊNCIA" in parecer_final or "ALERTA" in parecer_final:
            cor_box = "red"
        elif "⚠️" in parecer_final or "🟡" in parecer_final:
            cor_box = "orange"
        else:
            cor_box = "green"

        # --- EXIBIÇÃO ---
        st.markdown(f"""
        ### 🏥 Parecer Clínico Automatizado
        **Data do Parecer:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        **Identificação:** {nome} ({idade} anos)
        **Histórico:** G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}
        """)
        
        # Mostra o Parecer baseada na lógica acima
        if cor_box == "red":
            st.error(parecer_final)
        elif cor_box == "orange":
            st.warning(parecer_final)
        elif cor_box == "green":
            st.success(parecer_final)
        else:
            st.info(parecer_final)

        st.markdown("---")
        st.markdown("#### 📝 Detalhamento dos Dados Coletados")
        
        # Resumo das datas (verifica se foram preenchidas)
        if dum:
            texto_dum = f"DUM: {dum_str} (IG: {ig_str})"
        else:
            texto_dum = "DUM: Não informada"
        
        if dpp_eco:
            texto_usg = f"USG (DPP Eco): {dpp_eco_str} (IG: {ig_eco_str})"
        else:
            texto_usg = "USG: Não informada"

        st.markdown(f"""
        * **Datação:** {texto_dum} | {texto_usg}
        * **Bishop:** {score_bishop}
        * **Malinas:** {score_malinas}
        * **Vitalidade:** {ctg_class} | LA: {liquido}
        * **Fatores de Risco:** {', '.join(indicacoes_abs) if indicacoes_abs else 'Nenhum selecionado'}
        """)

        st.text_area("Conduta Médica e Prescrição (Digitável)", height=150, placeholder="Descreva o plano terapêutico, medicações prescritas e orientações...")
        
        st.caption("Documento gerado pelo sistema CesaSafe. Assinatura do Responsável: _________________________________")

if __name__ == "__main__":
    main()
