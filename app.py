import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta, timezone
from fpdf import FPDF
import io

# ==========================================
# FUNDAÇÃO: CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CesaScore: Apoio à Decisão", 
    page_icon="🤰", 
    layout="wide"
)

# Definindo o fuso horário padrão (Brasília)
FUSO_BRASILIA = timezone(timedelta(hours=-3))
HOJE_BRASILIA = datetime.now(FUSO_BRASILIA).date()

# ==========================================
# CÁLCULOS PREDITIVOS E CLÍNICOS
# ==========================================
def calcular_mfmu_vbac(idade, imc, parto_vaginal_previo, vbac_previo, motivo_cesarea_parada):
    if idade is None or imc is None:
        return None 
        
    intercepto = 3.515
    coef_idade = -0.035 * idade
    coef_imc = -0.063 * imc
    coef_vaginal = 0.816 if parto_vaginal_previo else 0
    coef_vbac = 1.047 if vbac_previo else 0
    coef_parada = -0.638 if motivo_cesarea_parada else 0
    
    w = intercepto + coef_idade + coef_imc + coef_vaginal + coef_vbac + coef_parada
    
    probabilidade = math.exp(w) / (1 + math.exp(w))
    return probabilidade * 100

def avaliar_dados_identificacao(idade, imc_atual, comorbidades, obstetricas, placenta_previa):
    fav = []
    risco = []
    
    # 1. Identificação de Fatores
    if idade is not None:
        if 18 <= idade < 35: fav.append("Idade materna em faixa de risco habitual.")
        elif idade >= 35: risco.append("Idade materna avançada.")
        elif idade < 15: risco.append("Adolescência precoce com restrição de desenvolvimento pélvico.")
    
    if imc_atual is not None:
        if 18.5 <= imc_atual < 25: fav.append("Índice de Massa Corporal (IMC) antropométrico adequado ao termo.")
        elif imc_atual >= 30: risco.append("Acúmulo de tecido adiposo (Obesidade) no momento do periparto.")
        elif imc_atual >= 25: risco.append("Sobrepeso materno no momento do parto.")
    
    for c in comorbidades: risco.append(f"Patologia sistêmica concomitante: {c}.")
    for o in obstetricas: risco.append(f"Intercorrência obstétrica associada: {o}.")

    if not fav: fav.append("Ausência de marcadores preditivos favoráveis isolados neste bloco basal.")
    if not risco: risco.append("Nenhum fator clínico ou biomecânico adicional detectado.")

    return fav, risco

# ==========================================
# FUNÇÃO AUXILIAR: GERADOR DE PDF
# ==========================================
class PDF(FPDF):
    def footer(self):
        self.set_y(-25)
        try:
            self.image("1.jpg", 70, self.get_y(), 20)
            self.image("2.png", 95, self.get_y(), 20)
            self.image("3.png", 120, self.get_y(), 20)
        except:
            pass

def gerar_pdf(relatorio_texto, data_hora_str):
    pdf = PDF()
    
    pdf.set_auto_page_break(True, margin=35)
    pdf.add_page()
    
    try:
        pdf.image("logo.png", 75, 8, 60)
        pdf.set_y(45) 
    except:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "CESASCORE - RELATÓRIO", 0, 1, 'C')
        pdf.ln(15)

    texto_latin = relatorio_texto.encode('latin-1', 'replace').decode('latin-1')
    
    bold_triggers = [
        "RELATÓRIO CLÍNICO DE APOIO",
        "PACIENTE:",
        "1. IDENTIFICAÇÃO",
        "Fatores favoráveis ao parto vaginal:",
        "Fatores favoráveis ao parto cesariano:",
        "2. CLASSIFICAÇÃO DE ROBSON",
        "3. ÍNDICE DE BISHOP",
        "4. AVALIAÇÃO PARA VBAC"
    ]
    bold_triggers = [t.encode('latin-1', 'replace').decode('latin-1') for t in bold_triggers]
    
    for linha in texto_latin.split('\n'):
        linha_limpa = linha.strip()
        
        if not linha_limpa:
            pdf.ln(2)
            continue
            
        if any(linha_limpa.startswith(trigger) for trigger in bold_triggers):
            pdf.set_font("Arial", 'B', 11)
            pdf.multi_cell(190, 6, linha, 0, 'L')
            pdf.set_font("Arial", '', 10)
            
        elif linha_limpa.startswith('(') and linha_limpa.endswith(')'):
            pdf.set_font("Arial", 'I', 9)
            pdf.multi_cell(190, 5, linha, 0, 'L')
            pdf.set_font("Arial", '', 10)
            
        else:
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(190, 5, linha, 0, 'L')
            
    pdf.ln(15) 
    
    if pdf.get_y() > 210:
        pdf.add_page()
    
    pdf.set_x(10)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_fill_color(200, 240, 200)
    
    aviso = "Aviso Legal: Ferramenta acadêmica de apoio baseada em protocolos assistenciais. A decisão clínica final é de responsabilidade do médico obstetra."
    aviso_latin = aviso.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(190, 5, aviso_latin, 0, 'L', True)
    
    pdf.ln(20) 
    y_assinatura = pdf.get_y()
    
    pdf.set_font("Arial", '', 10)
    texto_data = f"Relatório gerado em: {data_hora_str}".encode('latin-1', 'replace').decode('latin-1')
    pdf.set_xy(10, y_assinatura)
    pdf.cell(90, 5, texto_data, 0, 0, 'L')
    
    pdf.set_xy(120, y_assinatura)
    pdf.cell(80, 5, "________________________________________", 0, 1, 'C')
    pdf.set_x(120)
    pdf.cell(80, 5, "Profissional avaliador", 0, 1, 'C')
    
    return bytes(pdf.output(dest='S'), encoding='latin-1')

# ==========================================
# INÍCIO DO APLICATIVO PRINCIPAL
# ==========================================
def main():
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; }
        [data-testid="stHeader"] { background-color: transparent !important; }
        h1, h2, h4 { color: #0B3B60 !important; font-weight: 600 !important; }
        h3 { color: #1A6B7C !important; font-weight: 600 !important; font-size: 1.15rem !important; }
        .stButton > button[kind="primary"] {
            background-color: #1A6B7C !important; color: white !important; border-radius: 8px !important;
            border: none !important; padding: 0.5rem 1rem !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.3s ease !important; font-weight: bold !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #124B57 !important; transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1) !important;
        }
        div[data-testid="stMetricValue"] { color: #1A6B7C !important; }
        hr { border-top: 1px solid #E2E8F0 !important; }
        div[data-testid="stAlert"] { border-radius: 8px !important; border: none !important; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02) !important; }
        div[data-testid="stExpander"] {
            border-radius: 12px !important; border: 1px solid #F1F5F9 !important; background-color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important; margin-bottom: 1.5rem !important;
        }
        div[data-testid="stExpander"] summary p { font-size: 1.3rem !important; color: #0B3B60 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

    try:
        st.image("logo.png", width=500) 
    except:
        st.title("CesaScore")
    
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais. 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # BLOCO 1: IDENTIFICAÇÃO
    # ==========================================
    with st.expander("1. Identificação", expanded=True):
        data_minima = date(HOJE_BRASILIA.year - 60, 1, 1)
        data_maxima = HOJE_BRASILIA
        
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
            
        with c2:
            data_nasc = st.date_input("Data de Nascimento", value=None, min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
            
        with c3:
            idade = None
            if data_nasc:
                idade = HOJE_BRASILIA.year - data_nasc.year - ((HOJE_BRASILIA.month, HOJE_BRASILIA.day) < (data_nasc.month, data_nasc.day))
                st.metric("Idade", f"{idade} anos")

        imc = None
        imc_atual = None
        
        c4, c5, c6, c7 = st.columns(4)
        
        with c4:
            peso_pre_kg = st.number_input("Peso Pré-gestacional (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 70.5")
            
        with c5:
            peso_atual_kg = st.number_input("Peso Atual (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 80.0")
            
        with c6:
            altura_cm = st.number_input("Altura (cm)", min_value=100.0, max_value=250.0, value=None, step=1.0, format="%.0f", placeholder="Ex: 160")
            
        with c7:
            if altura_cm is not None and altura_cm > 0:
                altura_m = altura_cm / 100.0
                if peso_pre_kg is not None:
                    imc = peso_pre_kg / (altura_m ** 2)
                    st.metric("IMC Pré", f"{imc:.1f} kg/m²")
                if peso_atual_kg is not None:
                    imc_atual = peso_atual_kg / (altura_m ** 2)
                    st.metric("IMC Atual", f"{imc_atual:.1f} kg/m²")

    # ==========================================
    # BLOCO 2: HISTÓRICO OBSTÉTRICO
    # ==========================================
    with st.expander("2. Histórico Obstétrico", expanded=False):
        col_g, col_pn, col_pc, col_a = st.columns(4)
        with col_g:
            gestacoes = st.number_input("G (Gestações)", min_value=1, value=1, step=1)
        with col_pn:
            partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0, step=1)
        with col_pc:
            partos_cesareos = st.number_input("PC (Partos Cesáreos)", min_value=0, value=0, step=1)
        with col_a:
            abortos = st.number_input("A (Abortos)", min_value=0, value=0, step=1)

        tempo_cesarea = None
        motivo_cesarea_parada = False
        vbac_previo = False
        tem_cesarea_previa = (partos_cesareos > 0)
        teve_parto_vaginal_previo = (partos_normais > 0)
        
        if tem_cesarea_previa:
            st.warning("⚠️ Paciente com histórico de Parto Cesáreo Anterior (Avaliação para VBAC)")
            
            col_vbac1, col_vbac2 = st.columns(2)
            with col_vbac1:
                tempo_cesarea = st.radio(
                    "Há quanto tempo ocorreu o último parto cesáreo?",
                    ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
                )
            with col_vbac2:
                st.markdown("**Fatores Predicionais (MFMU):**")
                motivo_cesarea_parada = st.checkbox("Cesárea anterior foi por parada de progressão ou descida?")
                if teve_parto_vaginal_previo:
                    vbac_previo = st.checkbox("A paciente já teve um parto normal APÓS o parto cesáreo (VBAC prévio)?")
                else:
                    st.info("Paciente sem partos vaginais prévios registrados.")

        st.markdown("---") 
        
        col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
        dias_gest = 280 
        
        with col_dum:
            dum = st.date_input("DUM (Última Menstruação)", value=None, format="DD/MM/YYYY")
        
        with col_ig_dum:
            if dum:
                dias_gest = (HOJE_BRASILIA - dum).days 
                if dias_gest < 0: dias_gest = 0
                ig_sem = dias_gest // 7
                ig_dias = dias_gest % 7
                st.metric("IG (pela DUM)", f"{ig_sem} sem e {ig_dias} dias")
                
        with col_dpp_dum:
            if dum:
                dpp_calc = dum + timedelta(days=280)
                st.metric("DPP (pela DUM)", dpp_calc.strftime('%d/%m/%Y'))

        col_eco, col_ig_eco, col_vazia = st.columns(3)
        
        with col_eco:
            dpp_eco = st.date_input("DPP pela 1ª USG (Eco)", value=None, format="DD/MM/YYYY")
        
        with col_ig_eco:
            if dpp_eco:
                dt_concepcao_eco = dpp_eco - timedelta(days=280)
                dias_gest_eco = (HOJE_BRASILIA - dt_concepcao_eco).days
                if dias_gest_eco < 0: dias_gest_eco = 0
                ig_sem_eco = dias_gest_eco // 7
                ig_dias_eco = dias_gest_eco % 7
                st.metric("IG (pela USG)", f"{ig_sem_eco} sem e {ig_dias_eco} dias")
                dias_gest = dias_gest_eco

        st.markdown("---")
        
        col_comorb, col_obst = st.columns(2)
        
        with col_comorb:
            comorbidades_selecionadas = st.multiselect(
                "Comorbidades Maternas",
                options=["Hipertensão Crônica", "Diabetes Pré-gestacional", "Obesidade", "Cardiopatias", "Doença Renal Crônica", "Doença Autoimune", "Outras"],
                placeholder="Selecione as comorbidades...",
                max_selections=7
            )
            
            hipertensao = "Hipertensão Crônica" in comorbidades_selecionadas
            diabetes_previa = "Diabetes Pré-gestacional" in comorbidades_selecionadas
            obesidade_check = "Obesidade" in comorbidades_selecionadas
            cardiopatias = "Cardiopatias" in comorbidades_selecionadas
            doenca_renal = "Doença Renal Crônica" in comorbidades_selecionadas
            doenca_autoimune = "Doença Autoimune" in comorbidades_selecionadas
            outras_comorb = "Outras" in comorbidades_selecionadas
            
        with col_obst:
            obstetricas_selecionadas = st.multiselect(
                "Fatores Obstétricos da Gestação Atual",
                options=["Pré-eclâmpsia", "Diabetes Gestacional", "Placenta Prévia", "Gestação Gemelar", "Restrição de Crescimento Fetal", "Macrossomia Fetal", "Oligodrâmnio", "Polidrâmnio", "Apresentação Pélvica", "Apresentação Transversa"],
                placeholder="Selecione os fatores...",
                max_selections=10
            )
            
            pre_eclampsia = "Pré-eclâmpsia" in obstetricas_selecionadas
            diabetes_gest = "Diabetes Gestacional" in obstetricas_selecionadas
            placenta_previa = "Placenta Prévia" in obstetricas_selecionadas
            gemelar = "Gestação Gemelar" in obstetricas_selecionadas
            ciur = "Restrição de Crescimento Fetal" in obstetricas_selecionadas
            macrossomia = "Macrossomia Fetal" in obstetricas_selecionadas
            oligodramnio = "Oligodrâmnio" in obstetricas_selecionadas
            polidramnio = "Polidrâmnio" in obstetricas_selecionadas
            apres_pelvica = "Apresentação Pélvica" in obstetricas_selecionadas
            apres_transversa = "Apresentação Transversa" in obstetricas_selecionadas

    # ==========================================
    # BLOCO 3: EXAME FÍSICO E OBSTÉTRICO
    # ==========================================
    with st.expander("3. Exame Físico e Obstétrico", expanded=False):
        st.subheader("Avaliação Fetal e Dinâmica Uterina")
        col_fetos, col_sit, col_apres, col_tp = st.columns(4)
        
        with col_fetos:
            tipo_gestacao = st.selectbox("Número de Fetos", ["Único", "Múltiplo (Gêmeos ou mais)"])
        
        with col_sit:
            situacao = st.selectbox("Situação Fetal", ["Longitudinal", "Transversa", "Oblíqua"])
            
        with col_apres:
            apresentacao = st.selectbox("Apresentação Fetal", ["Cefálica", "Pélvica", "Córmica"])
        
        with col_tp:
            inicio_tp = st.selectbox("Início do Trabalho de Parto", ["Espontâneo", "Induzido", "Cesárea antes do TP"])
            
        col_au, col_bcf, col_du, col_vazia1 = st.columns(4)
        with col_au:
            au = st.number_input("AU (cm)", min_value=0, max_value=60, value=0, step=1, help="Altura Uterina")
        with col_bcf:
            bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140, step=1, help="Faixa de normalidade considerada: 120 a 160 bpm")
        with col_du:
            dinamica = st.number_input("Contrações / 10 min", min_value=0, max_value=10, value=0, step=1, help="Dinâmica Uterina (nº de contrações em 10 minutos)")

        st.markdown("---")

        st.subheader("Toque Vaginal")
        st.markdown("Preencha os dados do exame de toque para avaliação da maturidade cervical e progressão.")
        
        col_dilat, col_esvaec, col_altura = st.columns(3)
        with col_dilat:
            dilatacao = st.selectbox("Dilatação (cm)", ["Fechado (0 cm)", "1 a 2 cm", "3 a 4 cm", "5 cm ou mais"])
        with col_esvaec:
            esvaecimento = st.selectbox("Esvaecimento (%)", ["0 a 30%", "40 a 50%", "60 a 70%", "80% ou mais"])
        with col_altura:
            altura_apres = st.selectbox("Altura da Apresentação (De Lee)", ["-3", "-2", "-1", "0", "+1", "+2", "+3"])

        col_consist, col_posic, col_vazia3 = st.columns(3)
        with col_consist:
            consistencia = st.selectbox("Consistência do Colo", ["Firme", "Médio", "Amolecido"])
        with col_posic:
            posicao_colo = st.selectbox("Posição do Colo", ["Posterior", "Centralizado", "Anterior"])

    # ==========================================
    # BLOCO 4: RELATÓRIO FINAL DE APOIO À DECISÃO
    # ==========================================
    with st.expander("4. Relatório CesaScore", expanded=False):
        if st.button("Gerar Relatório de Apoio à Decisão", type="primary"):
            with st.spinner("Processando análise clínica..."):
                
                # --- LÓGICA DO TÓPICO 1 (NOVA ABORDAGEM CLÍNICA) ---
                lst_fav, lst_risco = avaliar_dados_identificacao(
                    idade, imc_atual, comorbidades_selecionadas, obstetricas_selecionadas, placenta_previa
                )
                
                # Substituindo '•' por hifens '-' para resolver o problema de encoding (?) no PDF
                formatados_fav = "\n".join([f"- {f}" for f in lst_fav])
                formatados_risco = "\n".join([f"- {f}" for f in lst_risco])

                # --- LÓGICA DO TÓPICO 2 (ROBSON - MANTIDA INTACTA) ---
                ig_robson = "Termo" if dias_gest >= 259 else "Pré-termo"
                paridade_total = partos_normais + partos_cesareos
                nulipara = (paridade_total == 0)
                multipara = (paridade_total > 0)
                
                grupo_robson = "Indefinido"
                descricao_robson = ""
                repercussao_robson = ""

                if tipo_gestacao == "Múltiplo (Gêmeos ou mais)":
                    grupo_robson = "Grupo 8"
                    descricao_robson = "Todas as gestantes com gestações múltiplas (incluindo cesárea prévia)."
                    repercussao_robson = "Alta taxa de parto cesáreo, dependendo diretamente da apresentação do primeiro feto e de protocolos institucionais."
                elif apresentacao in ["Córmica"] or situacao in ["Transversa", "Oblíqua"]:
                    grupo_robson = "Grupo 9"
                    descricao_robson = "Feto único em situação transversa ou oblíqua."
                    repercussao_robson = "Indicação ABSOLUTA de parto cesáreo na literatura atual. Via vaginal contraindicada."
                elif apresentacao == "Pélvica":
                    if nulipara:
                        grupo_robson = "Grupo 6"
                        descricao_robson = "Nulíparas, feto único, apresentação pélvica."
                    else:
                        grupo_robson = "Grupo 7"
                        descricao_robson = "Multíparas, feto único, apresentação pélvica."
                    repercussao_robson = "A presentation pélvica está fortemente associada à indicação de parto cesáreo eletivo na maioria dos serviços, salvo protocolos para Versão Cefálica Externa (VCE) bem-sucedida."
                elif ig_robson == "Pré-termo":
                    grupo_robson = "Grupo 10"
                    descricao_robson = "Feto único, presentation cefálica, pré-termo (< 37 semanas)."
                    repercussao_robson = "A via de parto prioritariamente recomendada é a vaginal. Contudo, devido à maior intolerância fetal às contrações (SFA), a taxa estatística de resolução por parto cesáreo é elevada."
                else:
                    if nulipara:
                        if inicio_tp == "Espontâneo":
                            grupo_robson = "Grupo 1"
                            descricao_robson = "Nulíparas, feto único, cefálico, >= 37 semanas, TP espontâneo."
                            repercussao_robson = "Excelente prognóstico. Espera-se alta taxa de sucesso para parto vaginal. O Ministério da Saúde orienta envidar esforços para evitar o primeiro parto cesáreo neste grupo."
                        else:
                            grupo_robson = "Grupo 2"
                            descricao_robson = "Nulíparas, feto único, cefálico, >= 37 semanas, induzido ou cesárea antes do TP."
                            repercussao_robson = "Risco substancialmente aumentado de parto cesáreo em razão do processo de indução em primigesta, especialmente se associado a colo uterino desfavorável (baixo escore de Bishop)."
                    elif multipara:
                        if tem_cesarea_previa:
                            grupo_robson = "Grupo 5"
                            descricao_robson = "Multíparas, feto único, cefálico, >= 37 semanas, com parto cesáreo prévio."
                            repercussao_robson = "Candidatas clássicas à prova de trabalho de parto (VBAC). O sucesso é viável, porém, na prática, este grupo concentra a maior parcela de partos cesáreos de repetição nos hospitais."
                        else:
                            if inicio_tp == "Espontâneo":
                                grupo_robson = "Grupo 3"
                                descricao_robson = "Multíparas (sem cesárea prévia), feto único, cefálico, >= 37 semanas, TP espontâneo."
                                repercussao_robson = "Altíssima probabilidade de parto vaginal rápido e bem-sucedido. O risco de parto cesáreo neste cenário clínico é o menor de todos os grupos."
                            else:
                                grupo_robson = "Grupo 4"
                                descricao_robson = "Multíparas (sem cesárea prévia), feto único, cefálico, >= 37 semanas, induzido ou cesárea antes do TP."
                                repercussao_robson = "Excelente probabilidade de parto vaginal pela multiparidade, porém a necessidade de indução eleva levemente o risco de falha comparado ao grupo 3."

                # --- LÓGICA DO TÓPICO 3 (BISHOP - MANTIDA INTACTA) ---
                pontos_bishop = 0
                if dilatacao == "1 a 2 cm": pontos_bishop += 1
                elif dilatacao == "3 a 4 cm": pontos_bishop += 2
                elif dilatacao == "5 cm ou mais": pontos_bishop += 3
                
                if esvaecimento == "40 a 50%": pontos_bishop += 1
                elif esvaecimento == "60 a 70%": pontos_bishop += 2
                elif esvaecimento == "80% ou mais": pontos_bishop += 3
                
                if altura_apres == "-2": pontos_bishop += 1
                elif altura_apres in ["-1", "0"]: pontos_bishop += 2
                elif altura_apres in ["+1", "+2", "+3"]: pontos_bishop += 3
                
                if consistencia == "Médio": pontos_bishop += 1
                elif consistencia == "Amolecido": pontos_bishop += 2
                
                if posicao_colo == "Centralizado": pontos_bishop += 1
                elif posicao_colo == "Anterior": pontos_bishop += 2
                
                status_bishop = "Desfavorável" if pontos_bishop <= 6 else "Favorável"
                repercussao_bishop = "O colo maduro favorece amplamente a progressão natural ou uma eventual indução, indicando alta probabilidade de desfecho vaginal com menor duração de trabalho de parto." if status_bishop == "Favorável" else "Colo imaturo. Maior risco de falha de indução e evolução para parto cesáreo por parada de progressão. A literatura indica a necessidade de preparo cervical prévio (ex: métodos mecânicos ou prostaglandinas)."

                # --- LÓGICA DO TÓPICO 4 (VBAC/MFMU - MANTIDA INTACTA) ---
                texto_vbac = ""
                conclusao_vbac = ""
                
                if tem_cesarea_previa:
                    fatores_vbac = []
                    if vbac_previo: fatores_vbac.append("Histórico de Parto Normal após parto cesáreo (Fator fortemente favorável)")
                    if motivo_cesarea_parada: fatores_vbac.append("Cesárea anterior por parada de progressão/descida (Fator desfavorável)")
                    if imc_atual and imc_atual >= 30: fatores_vbac.append("Obesidade atual (Fator desfavorável)")
                    if idade and idade >= 35: fatores_vbac.append("Idade >= 35 anos (Fator desfavorável)")
                    
                    if not fatores_vbac:
                        texto_vbac = "Nenhum fator preditor adverso ou positivo extremo identificado. O risco assume o padrão basal."
                        conclusao_vbac = "A paciente possui condições adequadas para a prova de trabalho de parto."
                    else:
                        texto_vbac = " | ".join(fatores_vbac)
                        if vbac_previo:
                            conclusao_vbac = "Predominância de fator favorável: O histórico de VBAC prévio eleva drasticamente a probabilidade estatística de novo sucesso (>80%). A conduta pende firmemente para tentativa de via vaginal."
                        else:
                            conclusao_vbac = "Presença de fatores desfavoráveis: O cenário atual compromete o índice de sucesso basal calculado pelo modelo estatístico."
                else:
                    texto_vbac = "Não aplicável. Paciente sem histórico de parto cesáreo."
                    conclusao_vbac = "Sem repercussão direta."

                # --- MONTAGEM FINAL ---
                nome_paciente = nome if nome else "Paciente não identificada"
                data_atual_str = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y às %H:%M")
                
                relatorio_final = f"""RELATÓRIO CLÍNICO DE APOIO À DECISÃO - CESASCORE
PACIENTE: {nome_paciente.upper()}

1. IDENTIFICAÇÃO

Fatores favoráveis ao parto vaginal:
{formatados_fav}

Fatores favoráveis ao parto cesariano:
{formatados_risco}

2. CLASSIFICAÇÃO DE ROBSON
(A Classificação de Robson é padronizada pela OMS para categorizar gestantes, monitorar taxas de parto cesáreo nos serviços e predizer a expectativa de via de parto.)
Identificado: {descricao_robson}
Classificação: {grupo_robson}
Repercussão na via de parto: {repercussao_robson}

3. ÍNDICE DE BISHOP
(O Índice de Bishop avalia clinicamente a maturidade cervical e prediz a probabilidade de sucesso de uma indução do trabalho de parto ou da sua progressão espontânea.)
Identificado: Colo {status_bishop} (Pontuação total: {pontos_bishop})
Repercussão na via de parto: {repercussao_bishop}

4. AVALIAÇÃO PARA VBAC (Parto Vaginal após Cesárea)
(O modelo matemático MFMU estima a probabilidade individualizada de sucesso de um parto normal após um parto cesáreo, servindo para o aconselhamento obstétrico embasado.)
Identificado: {texto_vbac}
Repercussão na via de parto: {conclusao_vbac}
"""
                st.success("Relatório de Apoio à Decisão gerado com sucesso!")
                st.text_area("Cópia de Texto Rápido (Prontuário):", relatorio_final, height=600)
                
                pdf_bytes = gerar_pdf(relatorio_final, data_atual_str)
                
                st.download_button(
                    label="📥 Baixar Laudo Completo em PDF",
                    data=pdf_bytes,
                    file_name=f"CesaScore_Relatorio_{nome_paciente.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )

    # --- INSERÇÃO DAS LOGOS NUMERADAS LADO A LADO NO SITE (RODAPÉ) ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_margem_esq, col1, col2, col3, col_margem_dir = st.columns([4, 1, 1, 1, 4])
    
    with col1:
        try:
            st.image("1.jpg", use_container_width=True)
        except:
            st.caption("CIPE")
            
    with col2:
        try:
            st.image("2.png", use_container_width=True)
        except:
            st.caption("UEPA")
            
    with col3:
        try:
            st.image("3.png", use_container_width=True)
        except:
            st.caption("CAPES")

    # ==========================================
    # INFORMAÇÕES DO RODAPÉ INSTITUCIONAL / AUTORIA
    # ==========================================
    st.markdown("---")
    
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    
    with col_f1:
        st.markdown("**CesarScore**")
        st.markdown("<div style='text-align: justify; font-size: 14px; color: gray;'>Aplicativo para predição da probabilidade de cirurgia cesariana utilizando escalas clínicas, desenvolvido para apoiar a tomada de decisão e qualificar a assistência obstétrica baseada em evidências científicas.</div>", unsafe_allow_html=True)

    with col_f2:
        st.markdown("**Sobre o Projeto**")
        st.markdown("<div style='text-align: justify; font-size: 14px; color: gray;'>Produto técnico desenvolvido por Juliana da Costa Furtado no âmbito do Programa de Pós-Graduação em Cirurgia e Pesquisa Experimental (PPG-CIPE), com foco na inovação tecnológica aplicada à saúde materna e na qualificação do cuidado obstétrico.</div>", unsafe_allow_html=True)

    with col_f3:
        st.markdown("**Contato**")
        st.markdown("<div style='font-size: 14px; color: gray;'>julianacostafurtado@gmail.com<br>Belém, Pará, Brasil</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 12px; color: gray;'>© 2026 Produto Técnico de Mestrado – CesarScore: Aplicativo para Predição de Cirurgia Cesariana Utilizando Escalas Clínicas.<br>Todos os direitos reservados.</div>", unsafe_allow_html=True)

# ==========================================
# COMANDO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()
