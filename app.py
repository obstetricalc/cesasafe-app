import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# Configuração da Página
st.set_page_config(page_title="CesaSafe: Apoio à Decisão", page_icon="🤰", layout="wide")

def main():
    st.title("🤰 CesaSafe: Sistema de Apoio à Decisão Obstétrica")
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico para apoio à decisão clínica, baseado em diretrizes (ACOG/MS). 
    A responsabilidade final é exclusivamente do profissional médico.
    """)
    st.markdown("---")

    # ==========================================
    # 1. IDENTIFICAÇÃO E ANAMNESE
    # ==========================================
    st.header("1. Identificação e Anamnese Obstétrica")
    c1, c2 = st.columns([2, 1])
    with c1: nome = st.text_input("Nome da Paciente")
    with c2: idade = st.number_input("Idade Materna (anos)", 10, 60, 25)

    st.markdown("**Histórico Obstétrico:**")
    cg, cpn, cpc, ca = st.columns(4)
    with cg: gestacoes = st.number_input("G (Gestações)", 1, 20, 1)
    with cpn: partos_normais = st.number_input("PN (Partos Vaginais)", 0, 20, 0)
    with cpc: partos_cesareos = st.number_input("PC (Cesáreas)", 0, 20, 0)
    with ca: abortos = st.number_input("A (Abortos)", 0, 20, 0)

    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Cesárea Anterior")
        tempo_cesarea = st.radio("Intervalo Interpartal:", ["< 2 anos (Curto)", "≥ 2 anos (Adequado)"])

    st.markdown("---")
    
    # ==========================================
    # 2. DATAÇÃO DA GESTAÇÃO
    # ==========================================
    st.subheader("📅 Cronologia e Datação")
    cdum, cig, cdpp = st.columns(3)
    
    # Lógica de Datação
    ig_final_sem = 0
    ig_final_dias = 0
    metodo_datacao = "Indefinido"
    
    with cdum: dum = st.date_input("DUM", value=None, format="DD/MM/YYYY")
    
    dum_txt, ig_dum_txt, dpp_dum_txt = "---", "---", "---"
    if dum:
        dum_txt = dum.strftime('%d/%m/%Y')
        days = (date.today() - dum).days
        if days >= 0:
            ig_final_sem, ig_final_dias = days // 7, days % 7
            metodo_datacao = "DUM"
            ig_dum_txt = f"{ig_final_sem}s {ig_final_dias}d"
            dpp_dum_txt = (dum + timedelta(days=280)).strftime('%d/%m/%Y')

    with cig: st.metric("IG (DUM)", ig_dum_txt)
    with cdpp: st.metric("DPP (DUM)", dpp_dum_txt)

    ceco, cigeco, cvazio = st.columns(3)
    with ceco: dpp_eco = st.date_input("DPP pela 1ª USG", value=None, format="DD/MM/YYYY")
    
    usg_txt, ig_usg_txt = "---", "---"
    if dpp_eco:
        usg_txt = dpp_eco.strftime('%d/%m/%Y')
        dt_conc = dpp_eco - timedelta(days=280)
        days_eco = (date.today() - dt_conc).days
        if days_eco >= 0:
            ig_eco_sem, ig_eco_dias = days_eco // 7, days_eco % 7
            ig_usg_txt = f"{ig_eco_sem}s {ig_eco_dias}d"
            # USG sobrepõe DUM se informada
            ig_final_sem, ig_final_dias = ig_eco_sem, ig_eco_dias
            metodo_datacao = "USG Precoce"

    with cigeco: st.metric("IG (USG)", ig_usg_txt)
    st.markdown("---")

    # ==========================================
    # 3. EXAME FÍSICO E FETAL
    # ==========================================
    st.header("3. Exame Físico e Fetal")
    c_au, c_bcf, c_sit, c_apres = st.columns(4)
    with c_au: au = st.number_input("AU (cm)", 0, 60, 0)
    with c_bcf: bcf = st.number_input("BCF (bpm)", 0, 250, 140, help="Ref: 110-160")
    with c_sit: situacao = st.selectbox("Situação", ["Longitudinal", "Transversa", "Oblíqua"])
    with c_apres: apresentacao = st.selectbox("Apresentação", ["Cefálica", "Pélvica", "Córmica"])
    st.markdown("---")

    # ==========================================
    # 4. ESCORES (BISHOP E MALINAS)
    # ==========================================
    st.header("4. Avaliação Cervical e Transporte")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: dilatacao = st.selectbox("Dilatação (cm)", [0,1,2,3], format_func=lambda x: ["0 (0)", "1-2 (1)", "3-4 (2)", "≥5 (3)"][x])
    with c2: apagamento = st.selectbox("Apagamento (%)", [0,1,2,3], format_func=lambda x: ["0-30 (0)", "40-50 (1)", "60-70 (2)", "≥80 (3)"][x])
    with c3: altura = st.selectbox("Altura (De Lee)", [0,1,2,3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1,0 (2)", "+1,+2 (3)"][x])
    with c4: consistencia = st.selectbox("Consistência", [0,1,2], format_func=lambda x: ["Firme (0)", "Média (1)", "Amolecida (2)"][x])
    with c5: posicao = st.selectbox("Posição", [0,1,2], format_func=lambda x: ["Posterior (0)", "Média (1)", "Anterior (2)"][x])
    score_bishop = dilatacao + apagamento + altura + consistencia + posicao
    
    m1, m2, m3 = st.columns(3)
    with m1: m_par = st.selectbox("Paridade (Malinas)", [0,1,2], format_func=lambda x: ["1 (0)", "2 (1)", "≥3 (2)"][x])
    with m2: m_dur = st.selectbox("Duração TP", [0,1,2], format_func=lambda x: ["<3h (0)", "3-5h (1)", ">6h (2)"][x])
    with m3: m_memb = st.selectbox("Membranas", [0,1,2], format_func=lambda x: ["Int. (0)", "Rot <1h (1)", "Rot >1h (2)"][x])
    score_malinas = m_par + m_dur + m_memb + dilatacao # Reusando dilatacao (aprox)
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Bishop Total", f"{score_bishop}/13")
    col_res2.metric("Malinas Total", score_malinas)
    st.markdown("---")

    # ==========================================
    # 5. VITALIDADE E FATORES DE RISCO
    # ==========================================
    st.header("5. Vitalidade e Riscos")
    cf, ci = st.columns(2)
    with cf:
        ctg = st.radio("CTG (NICHD)", ["Categoria I (Normal)", "Categoria II (Suspeito)", "Categoria III (Anormal)"])
        liq = st.selectbox("Líquido Amniótico", ["Claro", "Meconial Fluido", "Meconial Espesso", "Sanguinolento/Fétido"])
    with ci:
        riscos = st.multiselect("Fatores de Risco:", [
            "Nenhum", "Iteratividade (2+ Cesáreas)", "Placenta Prévia", "Herpes Ativo", 
            "DCP", "Sofrimento Fetal Agudo", "Pré-eclâmpsia/Eclâmpsia", 
            "HIV > 1000cp/Desconhecido", "Febre Materna"
        ])
    st.markdown("---")

    # ==========================================
    # RELATÓRIO DE INTELIGÊNCIA CLÍNICA
    # ==========================================
    if st.button("GERAR LAUDO OBSTÉTRICO COMPLETO", type="primary"):
        
        # --- PROCESSAMENTO ---
        
        # 1. Análise Cronológica
        analise_crono = []
        if ig_final_sem < 37:
            analise_crono.append(f"🔴 **Prematuridade ({ig_final_sem}s):** Risco de SDR. Necessário corticoide/neuroproteção se indicado.")
        elif ig_final_sem >= 41:
            analise_crono.append(f"🟠 **Pós-datismo ({ig_final_sem}s):** Risco de insuficiência placentária. Vigilância rigorosa.")
        else:
            analise_crono.append(f"🟢 **Termo ({ig_final_sem}s):** Idade gestacional oportuna para resolução.")

        # 2. Análise Fetal
        analise_fetal = []
        if bcf < 110: analise_fetal.append(f"🔴 **Bradicardia ({bcf} bpm):** Risco de hipóxia aguda.")
        elif bcf > 160: analise_fetal.append(f"🟠 **Taquicardia ({bcf} bpm):** Investigar infecção/hipóxia.")
        else: analise_fetal.append(f"🟢 **BCF Normal ({bcf} bpm).**")
        
        if apresentacao != "Cefálica": analise_fetal.append(f"🟠 **Apresentação {apresentacao}:** Atenção à via de parto.")

        # 3. Análise Vitalidade e Infecção
        analise_vital = []
        sinais_inf = 0
        if "Febre Materna" in riscos: sinais_inf += 1
        if bcf > 160: sinais_inf += 1
        if m_memb == 2: sinais_inf += 1 # Rotas > 1h
        if liq == "Sanguinolento/Fétido": sinais_inf += 2

        if "Categoria III" in ctg or "Sofrimento Fetal Agudo" in riscos:
            analise_vital.append("🔴 **Sofrimento Fetal Agudo:** Indicação de resolução imediata.")
        elif "Categoria II" in ctg:
            analise_vital.append("🟠 **CTG Suspeita:** Vigilância contínua e reanimação intrauterina.")
        
        if sinais_inf >= 2:
            analise_vital.append("🟠 **Risco de Corioamnionite:** Considerar antibiótico e resolução.")
        if liq == "Meconial Espesso":
            analise_vital.append("🟠 **Mecônio Espesso:** Risco de SAM. Equipe de Neo a postos.")

        # 4. Análise Cervical e Via de Parto
        analise_parto = []
        contraindica_vaginal = False
        contraindica_miso = False

        if "Placenta Prévia" in riscos or "Herpes Ativo" in riscos or "Iteratividade (2+ Cesáreas)" in riscos or "DCP" in riscos:
            contraindica_vaginal = True
            analise_parto.append("🔴 **Contraindicação ao Parto Vaginal:** (Placenta Prévia, Iteratividade, Herpes ou DCP).")
        
        if partos_cesareos > 0:
            contraindica_miso = True
            analise_parto.append("⚠️ **Cicatriz Uterina Prévia:** Misoprostol contraindicado. Risco de rotura.")
        
        if not contraindica_vaginal:
            if score_bishop < 6:
                if contraindica_miso:
                    analise_parto.append("🟠 **Colo Imaturo em Cesareada:** Maturação apenas mecânica (Foley) ou Cesárea.")
                else:
                    analise_parto.append("🟡 **Colo Imaturo:** Necessário preparo cervical (Misoprostol/Foley) para indução.")
            else:
                analise_parto.append("🟢 **Colo Maduro:** Favorável à indução com Ocitocina/Amniotomia.")

        # --- EXIBIÇÃO DO RELATÓRIO ---
        
        st.markdown(f"""
        ### 📄 LAUDO MÉDICO OBSTÉTRICO (CesaSafe)
        **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')} | **Paciente:** {nome} ({idade}a)
        **Diagnóstico Obstétrico:** G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos} | IG: {ig_final_sem}s {ig_final_dias}d
        """)

        st.info("### 1️⃣ Análise Cronológica e Fetal")
        for i in analise_crono: st.write(i)
        for i in analise_fetal: st.write(i)

        st.warning("### 2️⃣ Análise de Vitalidade e Riscos")
        if not analise_vital: st.write("✅ Sem alterações agudas de vitalidade detectadas.")
        for i in analise_vital: st.write(i)

        st.success("### 3️⃣ Avaliação de Via de Parto (Cérvice/Pelve)")
        for i in analise_parto: st.write(i)
        
        # CONCLUSÃO FINAL (SÍNTESE)
        st.markdown("---")
        st.header("🎯 CONCLUSÃO E CONDUTA SUGERIDA")
        
        nivel_final = "VERDE"
        texto_conclusao = ""
        
        # Lógica da Conclusão
        if "Categoria III" in ctg or "Sofrimento Fetal Agudo" in riscos or "Pré-eclâmpsia/Eclâmpsia" in riscos:
            nivel_final = "VERMELHO"
            texto_conclusao = "EMERGÊNCIA OBSTÉTRICA. Necessária estabilização e resolução imediata da gestação (Via mais rápida)."
        elif contraindica_vaginal:
            nivel_final = "LARANJA"
            texto_conclusao = "INDICAÇÃO DE CESÁREA. Fatores obstrutivos ou risco materno-fetal elevado para parto vaginal."
        elif score_malinas >= 10:
            nivel_final = "VERMELHO"
            texto_conclusao = "PARTO IMINENTE (PERÍODO EXPULSIVO). Assistência ao parto in loco. Não transportar."
        elif "Prematuridade" in analise_crono[0] and score_malinas >= 5:
            nivel_final = "LARANJA"
            texto_conclusao = "TRABALHO DE PARTO PREMATURO. Inibição/Neuroproteção/Corticoide conforme protocolo. Referenciar UTI Neo."
        elif score_bishop < 6 and not contraindica_vaginal:
             nivel_final = "AMARELO"
             texto_conclusao = "COLO DESFAVORÁVEL. Se houver indicação de parto, iniciar maturação cervical (Método conforme cicatriz uterina)."
        else:
             texto_conclusao = "GESTAÇÃO DE CURSO HABITUAL / COLO FAVORÁVEL. Seguir rotina de assistência ao trabalho de parto ou indução."

        if nivel_final == "VERMELHO":
            st.error(f"**CONDUTA:** {texto_conclusao}")
        elif nivel_final == "LARANJA":
            st.warning(f"**CONDUTA:** {texto_conclusao}")
        elif nivel_final == "AMARELO":
            st.info(f"**CONDUTA:** {texto_conclusao}")
        else:
            st.success(f"**CONDUTA:** {texto_conclusao}")

        st.text_area("Prescrição e Evolução Médica (Editável)", height=150)
        st.caption("Documento gerado eletronicamente pelo sistema CesaSafe.")

if __name__ == "__main__":
    main()
