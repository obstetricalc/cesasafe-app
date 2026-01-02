import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="CesaSafe: Apoio à Decisão", page_icon="🤰", layout="wide")

def main():
    st.title("🤰 CesaSafe: Sistema de Apoio à Decisão Obstétrica")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais (ACOG/MS). 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 1: DADOS CLÍNICOS E DATAÇÃO
    # ==========================================
    st.header("1. Identificação e Anamnese Obstétrica")
    
    c_dados1, c_dados2 = st.columns([2, 1])
    with c_dados1:
        nome = st.text_input("Nome da Paciente")
    with c_dados2:
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=25)

    st.markdown("**Histórico Obstétrico:**")
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g: gestacoes = st.number_input("G - Gestações", min_value=1, value=1)
    with col_pn: partos_normais = st.number_input("PN - Partos Vaginais", min_value=0, value=0)
    with col_pc: partos_cesareos = st.number_input("PC - Partos Cesáreos", min_value=0, value=0)
    with col_a: abortos = st.number_input("A - Abortos", min_value=0, value=0)

    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio(
            "Intervalo Interpartal (Tempo desde a última cesárea):",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("---")
    
    # --- DATAÇÃO ---
    st.subheader("📅 Cronologia e Datação")
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    # Variáveis Globais de Datação
    ig_final_semanas = 0
    ig_final_dias = 0
    metodo_datacao = "Não definido"

    # DUM
    ig_str = "---"
    dpp_str = "---"
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
        # Define IG base pela DUM inicialmente
        ig_final_semanas = ig_sem
        ig_final_dias = ig_dias
        metodo_datacao = "DUM"

    with col_ig_dum: st.metric("IG (Calculada pela DUM)", ig_str)
    with col_dpp_dum: st.metric("DPP (Provável)", dpp_str)

    # USG
    col_eco, col_ig_eco, col_vazio = st.columns(3)
    ig_eco_str = "---"
    dpp_eco_str = "Não informada"
    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (Data Provável ECO)", value=None, format="DD/MM/YYYY")
    if dpp_eco:
        dpp_eco_str = dpp_eco.strftime('%d/%m/%Y')
        dt_concepcao_eco = dpp_eco - timedelta(days=280)
        dias_gest_eco = (date.today() - dt_concepcao_eco).days
        if dias_gest_eco < 0: dias_gest_eco = 0
        ig_sem_eco = dias_gest_eco // 7
        ig_dias_eco = dias_gest_eco % 7
        ig_eco_str = f"{ig_sem_eco}s e {ig_dias_eco}d"
        # USG Precoce sobrepõe DUM se informada (Simplificação)
        ig_final_semanas = ig_sem_eco
        ig_final_dias = ig_dias_eco
        metodo_datacao = "USG"

    with col_ig_eco: st.metric("IG (Calculada pela USG)", ig_eco_str)
    
    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: BIOMETRIA E ESTÁTICA
    # ==========================================
    st.header("2. Biometria e Estática Fetal")
    col_au, col_bcf, col_sit, col_apres = st.columns(4)
    with col_au: au = st.number_input("Altura Uterina - AU (cm)", min_value=0, max_value=60, value=0)
    with col_bcf: bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, help="Faixa: 120-160 bpm")
    with col_sit: situacao = st.selectbox("Situação Fetal", ["Longitudinal", "Transversa", "Oblíqua"])
    with col_apres: apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Córmica"])

    st.markdown("---")

    # ==========================================
    # SEÇÃO 3: BISHOP
    # ==========================================
    st.header("3. Índice de Bishop (Maturação Cervical)")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: dilatacao = st.selectbox("Dilatação Cervical (cm)", options=[0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥ 5 cm (3)"][x])
    with c2: apagamento = st.selectbox("Apagamento Cervical (%)", options=[0, 1, 2, 3], format_func=lambda x: ["0-30% (0)", "40-50% (1)", "60-70% (2)", "≥ 80% (3)"][x])
    with c3: altura = st.selectbox("Altura (De Lee)", options=[0, 1, 2, 3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1/0 (2)", "+1/+2 (3)"][x])
    with c4: consistencia = st.selectbox("Consistência do Colo", options=[0, 1, 2], format_func=lambda x: ["Firme (0)", "Média (1)", "Amolecida (2)"][x])
    with c5: posicao = st.selectbox("Posição do Colo", options=[0, 1, 2], format_func=lambda x: ["Posterior (0)", "Média (1)", "Anterior (2)"][x])
    score_bishop = dilatacao + apagamento + altura + consistencia + posicao
    st.metric("Score de Bishop Total", f"{score_bishop}/13 pontos")

    # ==========================================
    # SEÇÃO 4: MALINAS
    # ==========================================
    st.header("4. Escore de Malinas (Transporte)")
    m1, m2, m3 = st.columns(3)
    with m1: m_paridade = st.selectbox("Paridade", [0, 1, 2], format_func=lambda x: ["1 parto (0)", "2 partos (1)", "≥3 partos (2)"][x])
    with m2: m_membrana = st.selectbox("Integridade das Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras (0)", "Rotas <1h (1)", "Rotas >1h (2)"][x])
    with m2: m_duracao = st.selectbox("Duração do TP", [0, 1, 2], format_func=lambda x: ["< 3h (0)", "3-5h (1)", "> 6h (2)"][x])
    with m3: m_distancia = st.selectbox("Dilatação/Descida", [0, 1, 2], format_func=lambda x: ["Alta/Fechada (0)", "Média (1)", "Baixa/Completa (2)"][x])
    score_malinas = m_paridade + m_duracao + m_membrana + m_distancia
    st.metric("Score de Malinas", score_malinas)

    st.markdown("---")

    # ==========================================
    # SEÇÃO 5: VITALIDADE E RISCOS
    # ==========================================
    st.header("5. Vitalidade Fetal e Riscos")
    col_fetal, col_indica = st.columns(2)
    with col_fetal:
        ctg_class = st.radio("Cardiotocografia (CTG - NICHD)", ("Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"))
        liquido = st.selectbox("Líquido Amniótico", ["Claro / Grumos Finos", "Meconial Fluido", "Meconial Espesso", "Sanguinolento/Fétido"])
    with col_indica:
        indicacoes_abs = st.multiselect("Fatores de Risco Presentes:", 
            ["Nenhum", "Placenta Prévia", "Iteratividade (2+ cesáreas)", "Herpes Genital Ativo", 
             "DCP (Desproporção)", "Sofrimento Fetal Agudo", "Pré-eclâmpsia/Eclâmpsia", 
             "HIV Carga Viral Desconhecida", "Febre Materna Intraparto"])

    # ==========================================
    # CÉREBRO CLÍNICO (PROCESSAMENTO)
    # ==========================================
    st.markdown("---")
    if st.button("GERAR ANÁLISE CLÍNICA COMPLETA", type="primary"):
        
        diagnosticos = []
        condutas = []
        nivel_alerta = 0 # 0=Verde, 1=Amarelo, 2=Laranja, 3=Vermelho

        # --- 1. ANÁLISE DE VITALIDADE E INFECÇÃO ---
        ctg_anormal = "Categoria III" in ctg_class or "Sofrimento Fetal" in indicacoes_abs
        ctg_indet = "Categoria II" in ctg_class
        mec_espesso = liquido == "Meconial Espesso"

        # Risco de Corioamnionite (Febre + Taqui + Bolsa Rota >1h)
        sinais_infeccao = 0
        if "Febre Materna Intraparto" in indicacoes_abs: sinais_infeccao += 1
        if bcf > 160: sinais_infeccao += 1
        if m_membrana == 2: sinais_infeccao += 1 # Rotas > 1h
        if liquido == "Sanguinolento/Fétido": sinais_infeccao += 2

        if ctg_anormal:
            diagnosticos.append("🚨 **SOFRIMENTO FETAL AGUDO:** Evidência de hipóxia grave.")
            condutas.append("- **Resolução Imediata:** Via de parto mais rápida (Cesárea de emergência ou parto vaginal instrumental se expulsivo).")
            condutas.append("- Reanimação intrauterina imediata (O2, decúbito lateral, suspender ocitocina).")
            nivel_alerta = 3
        elif ctg_indet and mec_espesso:
            diagnosticos.append("🟠 **Vitalidade Reservada:** CTG indeterminada com mecônio espesso.")
            condutas.append("- Alto risco de Síndrome de Aspiração Meconial. Preparar Neonatologia.")
            condutas.append("- Vigilância contínua. Considerar resolução se não houver progressão rápida.")
            nivel_alerta = 2
        elif sinais_infeccao >= 2:
            diagnosticos.append("🟠 **Suspeita de Corioamnionite:** Sinais clínicos sugestivos.")
            condutas.append("- Iniciar antibioticoterapia intraparto conforme protocolo.")
            condutas.append("- Abreviar o trabalho de parto. Antipirético se febre.")
            nivel_alerta = 2

        # --- 2. ANÁLISE DE TRABALHO DE PARTO E PREMATURIDADE ---
        is_prematuro = 0 < ig_final_semanas < 37
        is_posdatismo = ig_final_semanas >= 41
        
        if score_malinas >= 10:
            if is_prematuro:
                diagnosticos.append(f"🔴 **TRABALHO DE PARTO PREMATURO ({ig_final_semanas}sem):** Parto iminente.")
                condutas.append("- Neuroproteção (Sulfato de Magnésio) se < 32 sem.")
                condutas.append("- Prevenção de hipotermia do RN. Não transportar se nascimento previsto < 30min.")
                nivel_alerta = max(nivel_alerta, 3)
            else:
                diagnosticos.append("🔴 **Parto Iminente (Expulsivo):** Malinas elevado.")
                condutas.append("- Assistência ao parto in loco. Risco alto de parto no transporte.")
                nivel_alerta = max(nivel_alerta, 3)
        elif is_posdatismo:
             diagnosticos.append(f"ℹ️ **Gestação Pós-termo ({ig_final_semanas}sem):** Aumento de risco de insuficiência placentária.")
             condutas.append("- Monitoramento rigoroso do volume de líquido e vitalidade.")
             condutas.append("- Indicação formal de indução do parto (se sem contraindicações).")

        # --- 3. ANÁLISE DE VIA DE PARTO E CICATRIZ UTERINA ---
        iteratividade = "Iteratividade (2+ cesáreas)" in indicacoes_abs
        tem_cesarea = partos_cesareos > 0
        
        if iteratividade:
            diagnosticos.append("⚠️ **Iteratividade (2+ Cesáreas):** Contraindicação relativa/absoluta ao parto vaginal.")
            condutas.append("- Programação de Cesárea Eletiva/Urgência.")
            condutas.append("- Contraindicada indução com misoprostol ou ocitocina.")
            nivel_alerta = max(nivel_alerta, 2)
        elif tem_cesarea:
            if tempo_cesarea == "Menos de 2 anos (< 24 meses)":
                diagnosticos.append("⚠️ **Cesárea Anterior Recente:** Intervalo interpartal curto.")
                condutas.append("- Risco aumentado de rotura uterina. Monitorar cicatriz.")
            
            # Correlação Crítica: Bishop Ruim + Cesárea Prévia
            if score_bishop < 6:
                 diagnosticos.append("⚠️ **Colo Desfavorável em Pct com Cesárea Prévia:**")
                 condutas.append("- **ATENÇÃO:** O uso de Misoprostol é CONTRAINDICADO para maturação cervical (risco de rotura).")
                 condutas.append("- Opções: Maturação mecânica (Sonda Foley) ou Cesárea.")
                 nivel_alerta = max(nivel_alerta, 2)
            else:
                diagnosticos.append("🟢 **TOLAC Favorável:** Colo maduro em paciente com cesárea prévia.")
                condutas.append("- Candidata a parto vaginal. Monitorização contínua.")

        # --- 4. ANÁLISE DE APRESENTAÇÃO ---
        if apresentacao != "Cefálica":
            if score_malinas > 5 and apresentacao == "Pélvica":
                diagnosticos.append("🚨 **PARTO PÉLVICO EM ANDAMENTO:** Situação de alto risco.")
                condutas.append("- Acionar equipe experiente. Preparar manobras de Bracht/Mauriceau.")
                nivel_alerta = 3
            else:
                diagnosticos.append(f"⚠️ **Apresentação {apresentacao}:**")
                condutas.append("- Encaminhar para avaliação de via de parto (Cesárea ou VCE).")
                nivel_alerta = max(nivel_alerta, 2)

        # --- 5. BISHOP ISOLADO (Se não caiu nas regras acima) ---
        if score_bishop < 6 and not iteratividade and nivel_alerta < 2:
            diagnosticos.append("ℹ️ **Colo Imaturo (Bishop Baixo):**")
            condutas.append("- Para indução: Necessário maturação cervical (Misoprostol/Foley).")
        elif score_bishop >= 6 and nivel_alerta < 2:
            diagnosticos.append("ℹ️ **Colo Maduro:**")
            condutas.append("- Favorável à amniotomia ou ocitocina se necessário.")

        # --- GERAÇÃO DO TEXTO FINAL ---
        if not diagnosticos: diagnosticos.append("✅ Avaliação dentro dos parâmetros de normalidade.")
        if not condutas: condutas.append("- Manter conduta expectante e monitoramento de rotina.")

        # Box Colorido
        box_type = ["success", "warning", "warning", "error"][nivel_alerta] # 0=Green, 1=Yellow, 2=Orange, 3=Red
        
        st.markdown(f"""
        ### 🏥 Relatório de Análise Clínica - CesaSafe
        **Paciente:** {nome} ({idade}a) | **IG:** {ig_final_semanas}s {ig_final_dias}d | **G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}**
        """)

        # Container Principal
        with st.container():
            if nivel_alerta == 3:
                st.error("🚨 **SITUAÇÃO CRÍTICA / EMERGÊNCIA**")
            elif nivel_alerta == 2:
                st.warning("🟠 **ALTO RISCO / ATENÇÃO ESPECIAL**")
            elif nivel_alerta == 1:
                st.info("🟡 **RISCO MODERADO / ALERTA**")
            else:
                st.success("🟢 **BAIXO RISCO / ROTINA**")

            c_diag, c_cond = st.columns(2)
            with c_diag:
                st.markdown("#### 🔍 Diagnósticos e Alertas")
                for d in diagnosticos: st.write(d)
            
            with c_cond:
                st.markdown("#### 💉 Conduta Sugerida (Protocolo)")
                for c in condutas: st.write(c)

        st.markdown("---")
        st.caption("Resumo dos Parâmetros: Bishop: {} | Malinas: {} | BCF: {} | CTG: {}".format(score_bishop, score_malinas, bcf, ctg_class))
        st.text_area("Anotações Médicas Complementares", height=100)

if __name__ == "__main__":
    main()
