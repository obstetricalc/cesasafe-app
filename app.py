import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ObstetriCalc Pro: Apoio à Decisão",
    page_icon="🤰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÕES AUXILIARES ---
def calcular_ig(data_referencia):
    if not data_referencia:
        return 0, 0, "---"
    dias_gest = (date.today() - data_referencia).days
    if dias_gest < 0: dias_gest = 0
    semanas = dias_gest // 7
    dias = dias_gest % 7
    return semanas, dias, f"{semanas}s e {dias}d"

def classificar_robson(partos_normais, partos_cesareos, gestacoes, situacao_fetal, inicio_trabalho, ig_semanas):
    # Lógica simplificada para triagem de Robson
    # Nulliparous (Nulípara) = Gestações anteriores (viáveis) == 0 ou (PN=0 e PC=0)
    # Multiparous (Multípara) = PN > 0 ou PC > 0
    paridade = "Nulípara" if (partos_normais + partos_cesareos) == 0 else "Multípara"
    
    grupo = "Indeterminado (Avaliar Manualmente)"
    
    if paridade == "Nulípara":
        if situacao_fetal == "Cefálica" and ig_semanas >= 37:
            if inicio_trabalho == "Espontâneo": grupo = "Grupo 1"
            elif inicio_trabalho in ["Induzido", "Cesárea Antes do Trabalho de Parto"]: grupo = "Grupo 2"
    
    elif paridade == "Multípara" and partos_cesareos == 0:
        if situacao_fetal == "Cefálica" and ig_semanas >= 37:
            if inicio_trabalho == "Espontâneo": grupo = "Grupo 3"
            elif inicio_trabalho in ["Induzido", "Cesárea Antes do Trabalho de Parto"]: grupo = "Grupo 4"
            
    elif paridade == "Multípara" and partos_cesareos >= 1:
        if partos_cesareos == 1 and situacao_fetal == "Cefálica" and ig_semanas >= 37: grupo = "Grupo 5 (Cesárea Anterior)"
        elif partos_cesareos >= 1: grupo = "Grupo 5 ou superior (Iterativa)"
        
    if situacao_fetal == "Pélvica":
        grupo = "Grupo 6 (Nulípara)" if paridade == "Nulípara" else "Grupo 7 (Multípara)"
    
    if situacao_fetal in ["Transversa", "Oblíqua"]:
        grupo = "Grupo 9"
        
    if ig_semanas > 0 and ig_semanas < 37 and situacao_fetal == "Cefálica":
        grupo = "Grupo 10 (Prematuro)"

    return grupo

# --- APLICAÇÃO PRINCIPAL ---
def main():
    # --- SIDEBAR (REFERÊNCIAS) ---
    with st.sidebar:
        st.title("📚 Referências Rápidas")
        with st.expander("Índice de Bishop"):
            st.markdown("""
            | Pontos | Dilatação | Apagamento | Altura | Consist. | Posição |
            | :--- | :--- | :--- | :--- | :--- | :--- |
            | **0** | Fechado | 0-30% | -3 | Firme | Post. |
            | **1** | 1-2 cm | 40-50% | -2 | Média | Média |
            | **2** | 3-4 cm | 60-70% | -1/0 | Mole | Ant. |
            | **3** | ≥ 5 cm | ≥ 80% | +1/+2 | - | - |
            """)
        with st.expander("Escore de Malinas"):
             st.info("Usado para avaliar risco de parto no transporte/admissão.")

    # --- CABEÇALHO ---
    st.title("🤰 ObstetriCalc: Manejo Clínico & Qualificação")
    st.markdown("**Ferramenta de Apoio à Decisão Clínica (Baseada em ACOG/MS/Robson)**")
    
    tab_dados, tab_exames, tab_decisao = st.tabs(["📋 Dados Clínicos", "🔬 Exames & Vitalidade", "✅ Relatório Final"])

    # ---------------------------------------------------------------------
    # ABA 1: DADOS CLÍNICOS
    # ---------------------------------------------------------------------
    with tab_dados:
        st.subheader("Identificação e Obstetrícia")
        
        c1, c2 = st.columns([3, 1])
        nome = c1.text_input("Nome da Paciente")
        idade = c2.number_input("Idade", 10, 60, 25)

        st.markdown("---")
        st.markdown("**Histórico Obstétrico (G P A)**")
        
        cg, cp, cc, ca = st.columns(4)
        gestacoes = cg.number_input("G (Gestações)", 1, 20, 1)
        partos_normais = cp.number_input("PN (Normais)", 0, 20, 0)
        partos_cesareos = cc.number_input("PC (Cesáreas)", 0, 20, 0)
        abortos = ca.number_input("A (Abortos)", 0, 20, 0)

        # Alerta Cesárea Anterior
        tempo_cesarea = None
        if partos_cesareos > 0:
            st.warning(f"⚠️ Paciente com {partos_cesareos} Cesárea(s) Anterior(es)")
            tempo_cesarea = st.radio("Tempo Interpartal (última cesárea):", 
                                     ["< 24 meses (Curto)", "≥ 24 meses (Adequado)"], horizontal=True)

        st.markdown("---")
        st.subheader("📅 Datação da Gestação")
        
        cdum, cec, cig = st.columns(3)
        dum = cdum.date_input("DUM", value=None, format="DD/MM/YYYY")
        dpp_eco = cec.date_input("DPP pela 1ª USG", value=None, format="DD/MM/YYYY")

        # Lógica de cálculo de IG
        ig_final_str = "Indefinida"
        ig_semanas_calc = 0
        dpp_final = "---"

        if dpp_eco: # Preferência pela USG se disponível
            s, d, ig_str = calcular_ig(dpp_eco - timedelta(days=280))
            ig_final_str = ig_str
            ig_semanas_calc = s
            dpp_final = dpp_eco.strftime('%d/%m/%Y')
            cig.success(f"IG (USG): {ig_str}")
        elif dum:
            s, d, ig_str = calcular_ig(dum)
            ig_final_str = ig_str
            ig_semanas_calc = s
            dpp_final = (dum + timedelta(days=280)).strftime('%d/%m/%Y')
            cig.info(f"IG (DUM): {ig_str}")
        else:
            cig.warning("Informe DUM ou USG")

    # ---------------------------------------------------------------------
    # ABA 2: EXAMES, BISHOP E VITALIDADE
    # ---------------------------------------------------------------------
    with tab_exames:
        col_esq, col_dir = st.columns(2)
        
        with col_esq:
            st.subheader("💖 Vitalidade Fetal")
            
            # --- CORREÇÃO SOLICITADA: BCF 120-160 ---
            bcf = st.number_input("BCF (bpm) - Basal", min_value=0, max_value=250, value=140)
            if bcf > 0:
                if bcf < 120:
                    st.error("📉 BRADICARDIA FETAL (< 120 bpm)")
                elif bcf > 160:
                    st.error("📈 TAQUICARDIA FETAL (> 160 bpm)")
                else:
                    st.success("✅ BCF Normocardico (120-160 bpm)")
            
            ctg_class = st.selectbox("Classificação CTG (NICHD)", 
                ["Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"])
            
            liquido = st.radio("Líquido Amniótico", ["Claro", "Meconial Fluido", "Meconial Espesso"], horizontal=True)

        with col_dir:
            st.subheader("🔍 Exame Físico (Bishop)")
            dilatacao = st.selectbox("Dilatação", [0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥ 5 cm (3)"][x])
            apagamento = st.selectbox("Apagamento", [0, 1, 2, 3], format_func=lambda x: ["0-30% (0)", "40-50% (1)", "60-70% (2)", "≥ 80% (3)"][x])
            altura = st.selectbox("Altura (De Lee)", [0, 1, 2, 3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1/0 (2)", "+1/+2 (3)"][x])
            consistencia = st.selectbox("Consistência", [0, 1, 2], format_func=lambda x: ["Firme (0)", "Média (1)", "Mole (2)"][x])
            posicao = st.selectbox("Posição Colo", [0, 1, 2], format_func=lambda x: ["Post. (0)", "Med. (1)", "Ant. (2)"][x])
            
            score_bishop = dilatacao + apagamento + altura + consistencia + posicao
            st.metric("Score de Bishop", f"{score_bishop}/13")

        st.markdown("---")
        st.subheader("⚖️ Classificação de Robson (Parâmetros)")
        r1, r2 = st.columns(2)
        situacao_fetal = r1.selectbox("Situação/Apresentação", ["Cefálica", "Pélvica", "Transversa", "Oblíqua"])
        inicio_trabalho = r2.selectbox("Início do Trabalho de Parto", ["Espontâneo", "Induzido", "Cesárea Antes do Trabalho de Parto"])

    # ---------------------------------------------------------------------
    # ABA 3: RELATÓRIO E DECISÃO
    # ---------------------------------------------------------------------
    with tab_decisao:
        st.header("Relatório de Apoio à Decisão")
        
        # Classificação Automática de Robson
        robson_group = classificar_robson(partos_normais, partos_cesareos, gestacoes, situacao_fetal, inicio_trabalho, ig_semanas_calc)
        
        if st.button("GERAR PARECER CLÍNICO", type="primary"):
            
            # 1. Análise de Vitalidade (Prioridade Máxima)
            alertas = []
            conduta_sugerida = []
            cor_box = "blue"

            # BCF
            if bcf < 120 or bcf > 160:
                alertas.append(f"⚠️ **ALTERAÇÃO DE BCF ({bcf} bpm):** Risco de sofrimento fetal. Avaliar variabilidade e acelerações.")
            
            # CTG
            if ctg_class == "Categoria III (Anormal)":
                alertas.append("🚨 **CTG CATEGORIA III:** Risco iminente de acidemia fetal. Parto imediato indicado.")
                cor_box = "red"
            elif ctg_class == "Categoria II (Indeterminado)":
                alertas.append("🔸 **CTG CATEGORIA II:** Necessita vigilância contínua e medidas de reanimação intrauterina.")
            
            # Mecônio
            if liquido == "Meconial Espesso":
                alertas.append("💩 **MECÔNIO ESPESSO:** Alerta para SAM. Equipe de Neo deve estar presente.")

            # Robson & Via de Parto
            if "Grupo 1" in robson_group or "Grupo 3" in robson_group:
                conduta_sugerida.append(f"✅ **Robson {robson_group}:** Baixo risco para cesárea. Favorecer parto vaginal.")
            elif "Grupo 5" in robson_group:
                conduta_sugerida.append(f"⚠️ **Robson {robson_group}:** Cesárea anterior. Candidata a TOLAC (Prova de Trabalho de Parto) se cicatriz uterina permitir e sem sinais de ruptura.")
            elif "Grupo 9" in robson_group or "Grupo 6" in robson_group or "Grupo 7" in robson_group:
                 conduta_sugerida.append(f"🛑 **Robson {robson_group}:** Situação fetal anômala (Pélvica/Transversa). Indicação formal de cesárea na maioria dos protocolos.")

            # Bishop
            if score_bishop < 6 and inicio_trabalho == "Induzido":
                conduta_sugerida.append(f"💊 **Colo Desfavorável (Bishop {score_bishop}):** Se indicação de parto, necessário maturação cervical (Misoprostol/Foley) antes da ocitocina.")

            # Renderização do Parecer
            st.markdown("### 🏥 Resumo do Caso")
            st.write(f"**Paciente:** {nome} ({idade} anos) | **IG:** {ig_final_str}")
            st.write(f"**Histórico:** G{gestacoes} P{partos_normais} C{partos_cesareos} A{abortos}")
            st.info(f"📊 **Classificação de Robson Estimada:** {robson_group}")
            
            if alertas:
                for a in alertas:
                    st.error(a)
            
            if conduta_sugerida:
                st.markdown("#### 🧭 Sugestões de Manejo (Baseado em Protocolo)")
                for c in conduta_sugerida:
                    st.markdown(f"- {c}")
            
            st.markdown("---")
            st.text_area("✍️ Evolução Médica / Prescrição", height=200, 
                         placeholder="Digite aqui a conduta final, medicações e plano de cuidados...")
            
            st.caption(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}. Documento auxiliar.")

if __name__ == "__main__":
    main()
