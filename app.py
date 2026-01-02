import streamlit as st
from datetime import date, timedelta, datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CesaSafe - Prontuário", page_icon="🤰", layout="wide")

# --- FUNÇÕES AUXILIARES ---

def calcular_ig_dum(dum):
    hoje = date.today()
    dias_totais = (hoje - dum).days
    semanas = dias_totais // 7
    dias = dias_totais % 7
    dpp = dum + timedelta(days=280)
    return weeks_days_to_string(semanas, dias), semanas, dias, dpp

def calcular_ig_usg(data_usg, semanas_usg, dias_usg):
    hoje = date.today()
    dias_passados = (hoje - data_usg).days
    dias_totais_gestacao = (semanas_usg * 7) + dias_usg + dias_passados
    semanas_atuais = dias_totais_gestacao // 7
    dias_atuais = dias_totais_gestacao % 7
    # DPP baseada na USG: data da USG - dias de gestação na época + 280
    data_concepcao_estimada = data_usg - timedelta(days=(semanas_usg * 7 + dias_usg))
    dpp = data_concepcao_estimada + timedelta(days=280)
    return weeks_days_to_string(semanas_atuais, dias_atuais), semanas_atuais, dias_atuais, dpp

def weeks_days_to_string(weeks, days):
    return f"{weeks} semanas e {days} dias"

def classificar_termo(semanas):
    if semanas < 37: return "Pré-termo"
    elif 37 <= semanas < 42: return "Termo"
    else: return "Pós-termo"

def calcular_robson(paridade, cesareas, num_fetos, apresentacao, ig_semanas, inicio_trabalho):
    # Lógica simplificada de Robson
    if apresentacao != "Cefálica":
        if apresentacao == "Transversa/Oblíqua": return 9
        if apresentacao == "Pélvica": return 6 if paridade == 0 else 7
    if num_fetos > 1: return 8
    if ig_semanas < 37: return 10
    if cesareas > 0: return 5
    # Cefálico, Único, >=37s, Sem cesárea prévia
    if paridade == 0: 
        return 1 if inicio_trabalho == "Espontâneo" else 2
    else: 
        return 3 if inicio_trabalho == "Espontâneo" else 4

# --- APP PRINCIPAL ---
def main():
    # MENU LATERAL
    with st.sidebar:
        st.title("🤰 CesaSafe")
        st.info("**Sistema de Apoio à Decisão Clínica**")
        st.markdown("---")
        st.write("Responsável Técnico:")
        profissional = st.text_input("Nome do Profissional", placeholder="Dr(a). Nome Sobrenome")
        crm_coren = st.text_input("Registro (CRM/COREN)")
        st.markdown("---")
        modo_impressao = st.checkbox("🖨️ Modo de Impressão (Relatório Limpo)")

    # CABEÇALHO
    if not modo_impressao:
        st.title("Prontuário Obstétrico & Calculadora de Risco")
        st.markdown("**Versão 3.0** - Identificação, Datação, Histórico e Escores.")
    else:
        st.markdown("## 🏥 Relatório de Admissão Obstétrica - CesaSafe")
        st.markdown(f"**Data do Atendimento:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.markdown(f"**Profissional:** {profissional} | **Registro:** {crm_coren}")

    st.markdown("---")

    # --- 1. IDENTIFICAÇÃO E OBSTETRÍCIA ---
    st.header("1. Identificação e Datação")
    
    col_id1, col_id2, col_id3 = st.columns(3)
    with col_id1:
        nome = st.text_input("Nome da Gestante")
    with col_id2:
        idade = st.number_input("Idade Materna", 10, 60, 25)
    with col_id3:
        risco_gestacional = st.selectbox("Estratificação de Risco", ["Baixo Risco", "Alto Risco"])
        local_parto = st.text_input("Local Previsto para o Parto", "Maternidade de Referência")

    # CÁLCULO DE IDADE GESTACIONAL
    st.subheader("Cálculo da Idade Gestacional (IG)")
    metodo_ig = st.radio("Método Prioritário para IG:", ["DUM (Data da Última Menstruação)", "USG Precoce"], horizontal=True)
    
    ig_atual_texto = ""
    ig_semanas_calc = 0
    dpp_calc = date.today()
    classificacao_termo = ""

    c_dat1, c_dat2 = st.columns(2)
    
    if metodo_ig == "DUM (Data da Última Menstruação)":
        with c_dat1:
            dum = st.date_input("Data da DUM", value=date.today() - timedelta(days=280))
            dum_confiavel = st.checkbox("DUM é confiável?", value=True)
        if dum_confiavel:
            ig_atual_texto, ig_semanas_calc, _, dpp_calc = calcular_ig_dum(dum)
    
    else: # USG
        with c_dat1:
            data_usg = st.date_input("Data da USG realizada")
        with c_dat2:
            c_usg1, c_usg2 = st.columns(2)
            ig_usg_sem = c_usg1.number_input("IG na USG (Semanas)", 4, 42, 12)
            ig_usg_dias = c_usg2.number_input("IG na USG (Dias)", 0, 6, 0)
        ig_atual_texto, ig_semanas_calc, _, dpp_calc = calcular_ig_usg(data_usg, ig_usg_sem, ig_usg_dias)

    # Exibir Resultado da Datação
    classificacao_termo = classificar_termo(ig_semanas_calc)
    st.success(f"**IG Atual:** {ig_atual_texto} | **DPP:** {dpp_calc.strftime('%d/%m/%Y')} | **Classificação:** {classificacao_termo}")

    st.markdown("---")

    # --- 2. HISTÓRICO OBSTÉTRICO DETALHADO ---
    st.header("2. Histórico Obstétrico")
    
    c_hist1, c_hist2, c_hist3, c_hist4 = st.columns(4)
    gestacoes = c_hist1.number_input("G (Gestações Totais)", 1, 20, 1)
    partos_vaginais = c_hist2.number_input("Partos Vaginais", 0, 20, 0)
    cesareas_previas = c_hist3.number_input("Cesáreas Anteriores", 0, 20, 0)
    abortos = c_hist4.number_input("A (Abortos)", 0, 20, 0)

    # Análise de Cicatriz / Rotura
    alerta_rotura = None
    msg_cicatriz = ""
    
    if cesareas_previas > 0:
        st.markdown("#### ⚠️ Detalhes da Cesariana Anterior")
        c_ces1, c_ces2, c_ces3 = st.columns(3)
        with c_ces1:
            data_ultima_cesarea = st.date_input("Data da Última Cesárea", value=date.today() - timedelta(days=730))
            # Calculo intervalo interpartal
            intervalo_meses = (date.today() - data_ultima_cesarea).days / 30
        with c_ces2:
            tipo_cicatriz = st.selectbox("Tipo de Cicatriz Uterina", ["Segmentar Transversa (Baixa)", "Corporal / Clássica", "T-Invertido", "Desconhecida"])
        with c_ces3:
            indicacao_anterior = st.text_input("Indicação da Cesárea Anterior")

        # Lógica de Risco de Rotura
        riscos = []
        if tipo_cicatriz in ["Corporal / Clássica", "T-Invertido"]:
            riscos.append("Cicatriz de Alto Risco (Corporal/T)")
        if intervalo_meses < 18:
            riscos.append(f"Intervalo Interpartal Curto ({int(intervalo_meses)} meses)")
        
        if riscos:
            alerta_rotura = "ALTO RISCO DE ROTURA UTERINA"
            msg_cicatriz = f"Fatores: {', '.join(riscos)}. Contraindicação relativa/absoluta à prova de trabalho de parto."
        else:
            msg_cicatriz = f"Intervalo: {int(intervalo_meses)} meses. Cicatriz Segmentar. Candidata à TOLAC (Trial of Labor) se condições favoráveis."

    # --- 3. DADOS ATUAIS (BISHOP/MALINAS/ROBSON) ---
    st.markdown("---")
    st.header("3. Avaliação Clínica Atual")

    col_fetos, col_apres, col_inicio = st.columns(3)
    num_fetos = col_fetos.selectbox("Nº Fetos", [1, 2, 3], format_func=lambda x: "Único" if x==1 else "Múltiplo")
    apresentacao = col_apres.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Transversa/Oblíqua"])
    inicio_tp = col_inicio.selectbox("Início do TP", ["Espontâneo", "Induzido", "Cesárea Antes do TP"])

    st.subheader("Índice de Bishop")
    b1, b2, b3, b4, b5 = st.columns(5)
    dilatacao = b1.selectbox("Dilatação", [0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥5 cm (3)"][x])
    apagamento = b2.selectbox("Apagamento", [0, 1, 2, 3], format_func=lambda x: ["0-30% (0)", "40-50% (1)", "60-70% (2)", "≥80% (3)"][x])
    altura = b3.selectbox("Altura (De Lee)", [0, 1, 2, 3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1, 0 (2)", "+1, +2 (3)"][x])
    consistencia = b4.selectbox("Consistência", [0, 1, 2], format_func=lambda x: ["Firme (0)", "Média (1)", "Mole (2)"][x])
    posicao = b5.selectbox("Posição", [0, 1, 2], format_func=lambda x: ["Posterior (0)", "Média (1)", "Anterior (2)"][x])
    score_bishop = dilatacao + apagamento + altura + consistencia + posicao

    st.subheader("Escore de Malinas")
    m1, m2, m3, m4 = st.columns(4)
    mal_paridade = m1.selectbox("Paridade (Malinas)", [0, 1, 2], format_func=lambda x: ["1 parto (0)", "2 partos (1)", "≥3 partos (2)"][x])
    mal_tempo = m2.selectbox("Duração do TP", [0, 1, 2], format_func=lambda x: ["<3h (0)", "3-5h (1)", ">6h (2)"][x])
    mal_memb = m3.selectbox("Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras (0)", "Rotas recente (1)", "Rotas >1h (2)"][x])
    mal_desc = m4.selectbox("Distância/Descida", [0, 1, 2], format_func=lambda x: ["Alta (0)", "Média (1)", "Baixa (2)"][x])
    score_malinas = mal_paridade + mal_tempo + mal_memb + mal_desc

    # --- CÁLCULO ROBSON ATUALIZADO ---
    # Paridade para Robson: 0 se (Parto Normal + Cesarea) == 0, senão 1
    paridade_robson = 0 if (partos_vaginais + cesareas_previas) == 0 else 1
    robson_group = calcular_robson(paridade_robson, cesareas_previas, num_fetos, apresentacao, ig_semanas_calc, inicio_tp)

    # --- 4. RELATÓRIO FINAL ---
    st.markdown("---")
    if not modo_impressao:
        st.markdown("### 📝 Relatório Final Gerado")
    
    with st.container():
        # Bloco visual de resumo
        r1, r2, r3 = st.columns(3)
        r1.metric("IG Atual", ig_atual_texto, classificacao_termo)
        r2.metric("Grupo de Robson", f"Grupo {robson_group}")
        r3.metric("Bishop", f"{score_bishop} pts", "Favorável" if score_bishop >= 6 else "Desfavorável")

        st.markdown(f"""
        **Resumo Obstétrico:** G{gestacoes} P{partos_vaginais} C{cesareas_previas} A{abortos}
        """)

        if cesareas_previas > 0:
            if alerta_rotura:
                st.error(f"🚨 **ALERTA:** {alerta_rotura}")
                st.write(f"**Análise:** {msg_cicatriz}")
            else:
                st.info(f"**Status Cicatriz Uterina:** {msg_cicatriz}")

        # Conduta
        st.write("---")
        st.write("**Estratificação de Risco:** " + risco_gestacional)
        st.write("**Local Previsto:** " + local_parto)
        
        st.text_area("Evolução Clínica e Conduta Médica:", height=150, placeholder="Descreva o exame físico, BCF, dinâmica uterina e plano terapêutico.")
        
        if modo_impressao:
            st.caption("Documento assinado digitalmente pelo sistema CesaSafe.")
            st.markdown("______________________________________")
            st.markdown(f"**{profissional}**")
            st.markdown(f"{crm_coren}")

if __name__ == "__main__":
    main()
