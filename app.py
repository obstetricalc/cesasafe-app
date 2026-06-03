import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta
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

# ==========================================
# FUNÇÃO AUXILIAR: GERADOR DE PDF
# ==========================================
def gerar_pdf(relatorio_texto, data_hora_str):
    pdf = FPDF()
    pdf.add_page()
    
    # Tenta inserir a logo
    try:
        pdf.image("logo.png", x=10, y=8, w=60)
        pdf.ln(25)
    except:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="CESASCORE - RELATORIO", ln=True, align='C')
        pdf.ln(10)

    # Cabeçalho de Data e Hora
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, txt=f"Relatorio gerado em: {data_hora_str}", ln=True, align='R')
    pdf.ln(5)

    # Corpo do texto com inteligência de leitura de linhas
    pdf.set_font("Arial", size=11)
    texto_latin = relatorio_texto.encode('latin-1', 'replace').decode('latin-1')
    
    for linha in texto_latin.split('\n'):
        linha_limpa = linha.strip()
        # Se a linha estiver entre parênteses, imprime em letra menor e itálico
        if linha_limpa.startswith('(') and linha_limpa.endswith(')'):
            pdf.set_font("Arial", 'I', 9)
            pdf.multi_cell(0, 5, txt=linha)
            pdf.set_font("Arial", '', 11) # Volta ao normal
        else:
            pdf.multi_cell(0, 6, txt=linha)
    
    # Aviso Legal no Rodapé
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 9)
    aviso = "Aviso Legal: Esta ferramenta e um prototipo academico auxiliar, baseado em protocolos assistenciais. A decisao clinica final e de responsabilidade exclusiva do medico obstetra."
    pdf.multi_cell(0, 5, txt=aviso)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# INÍCIO DO APLICATIVO PRINCIPAL
# ==========================================
def main():
    # --- CABEÇALHO ---
    st.image("logo.png", width=500) 
    
    st.markdown("""
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais. 
    A decisão clínica final é de responsabilidade exclusiva do médico obstetra.
    """)
    st.markdown("---")

    # ==========================================
    # BLOCO 1: IDENTIFICAÇÃO
    # ==========================================
    st.header("1. Identificação")
    
    hoje = date.today()
    data_minima = date(hoje.year - 60, 1, 1)
    data_maxima = hoje
    
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c2:
        data_nasc = st.date_input("Data de Nascimento", value=None, min_value=data_minima, max_value=data_maxima, format="DD/MM/YYYY")
        
    with c3:
        idade = None
        if data_nasc:
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.metric("Idade", f"{idade} anos")

    c4, c5, c6 = st.columns(3)
    
    with c4:
        peso_pre_kg = st.number_input("Peso Pré-gestacional (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 70.5")
        
    with c5:
        altura_m = st.number_input("Altura (metros)", min_value=1.00, max_value=2.50, value=None, step=0.01, format="%.2f", placeholder="Ex: 1.60")
        
    with c6:
        imc = None
        if peso_pre_kg is not None and altura_m is not None and altura_m > 0:
            imc = peso_pre_kg / (altura_m ** 2)
            st.metric("IMC Pré-gestacional", f"{imc:.1f} kg/m²")

    st.markdown("---")
    # --- FIM DO BLOCO 1 ---

    # ==========================================
    # BLOCO 2: HISTÓRICO OBSTÉTRICO
    # ==========================================
    st.header("2. Histórico Obstétrico")
    
    # --- Gestas e Paridade ---
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1, step=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0, step=1)
    with col_pc:
        partos_cesareos = st.number_input("PC (Partos Cesáreos)", min_value=0, value=0, step=1)
    with col_a:
        abortos = st.number_input("A (Abortos)", min_value=0, value=0, step=1)

    # --- Alerta Interativo de Parto Cesáreo Anterior e Dados VBAC ---
    tempo_cesarea = None
    motivo_cesarea_parada = False
    vbac_previo = False
    
    if partos_cesareos > 0:
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
            if partos_normais > 0:
                vbac_previo = st.checkbox("A paciente já teve um parto normal APÓS a cesárea (VBAC prévio)?")
            else:
                st.info("Paciente sem partos vaginais prévios registados.")

    st.markdown("") 
    
    # --- Datação da Gestação (DUM) ---
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    with col_dum:
        dum = st.date_input("DUM (Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    with col_ig_dum:
        if dum:
            dias_gest = (hoje - dum).days 
            if dias_gest < 0: dias_gest = 0
            ig_sem = dias_gest // 7
            ig_dias = dias_gest % 7
            st.metric("IG (pela DUM)", f"{ig_sem} sem e {ig_dias} dias")
            
    with col_dpp_dum:
        if dum:
            dpp_calc = dum + timedelta(days=280)
            st.metric("DPP (pela DUM)", dpp_calc.strftime('%d/%m/%Y'))

    # --- Datação da Gestação (USG) ---
    col_eco, col_ig_eco, col_vazia = st.columns(3)
    
    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (Eco)", value=None, format="DD/MM/YYYY")
    
    with col_ig_eco:
        if dpp_eco:
            dt_concepcao_eco = dpp_eco - timedelta(days=280)
            dias_gest_eco = (hoje - dt_concepcao_eco).days
            if dias_gest_eco < 0: dias_gest_eco = 0
            ig_sem_eco = dias_gest_eco // 7
            ig_dias_eco = dias_gest_eco % 7
            st.metric("IG (pela USG)", f"{ig_sem_eco} sem e {ig_dias_eco} dias")

    st.markdown("")
    
    # --- Comorbidades e Fatores de Risco ---
    col_comorb, col_obst = st.columns(2)
    
    with col_comorb:
        st.markdown("**Comorbidades Maternas**")
        hipertensao = st.checkbox("Hipertensão Crônica")
        diabetes_previa = st.checkbox("Diabetes Pré-gestacional")
        obesidade_check = st.checkbox("Obesidade")
        cardiopatias = st.checkbox("Cardiopatias")
        doenca_renal = st.checkbox("Doença Renal Crônica")
        doenca_autoimune = st.checkbox("Doença Autoimune")
        outras_comorb = st.checkbox("Outras")
        
    with col_obst:
        st.markdown("**Fatores Obstétricos da Gestação Atual**")
        pre_eclampsia = st.checkbox("Pré-eclâmpsia")
        diabetes_gest = st.checkbox("Diabetes Gestacional")
        placenta_previa = st.checkbox("Placenta Prévia")
        gemelar = st.checkbox("Gestação Gemelar")
        ciur = st.checkbox("Restrição de Crescimento Fetal")
        macrossomia = st.checkbox("Macrossomia Fetal")
        oligodramnio = st.checkbox("Oligodrâmnio")
        polidramnio = st.checkbox("Polidrâmnio")
        apres_pelvica = st.checkbox("Apresentação Pélvica")
        apres_transversa = st.checkbox("Apresentação Transversa")

    st.markdown("---")
    # --- FIM DO BLOCO 2 ---

    # ==========================================
    # BLOCO 3: EXAME FÍSICO E OBSTÉTRICO
    # ==========================================
    st.header("3. Exame Físico e Obstétrico")
    
    # --- Avaliação Fetal e Dinâmica Uterina ---
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

    st.markdown("")

    # --- Toque Vaginal (Avaliação do Colo Uterino) ---
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

    st.markdown("---")
    # --- FIM DO BLOCO 3 ---

    # ==========================================
    # BLOCO 4: RELATÓRIO FINAL DE APOIO À DECISÃO
    # ==========================================
    st.header("4. Relatório CesaScore")
    
    if st.button("Gerar Relatório de Apoio à Decisão", type="primary"):
        with st.spinner("Processando dados e interpretando diretrizes clínicas..."):
            
            # --- 1. AVALIAÇÃO CLÍNICA MATERNA E RISCOS ---
            texto_idade = "Idade nao informada."
            if idade:
                if idade >= 35:
                    texto_idade = f"Idade: {idade} anos (Idade Materna Avancada).\nPredicao de via de parto: A literatura aponta maior incidencia de comorbidades (DHEG, DMG) e risco de distocia funcional. Embora o parto vaginal seja viavel e encorajado, estatisticamente ha aumento significativo nas taxas de evolucao para parto cesareo."
                elif idade < 15:
                    texto_idade = f"Idade: {idade} anos (Adolescencia Precoce).\nPredicao de via de parto: Maior risco de desproporcao cefalopelvica. A via de parto depende do desenvolvimento pelvico, havendo taxas elevadas de resolucao por via cirurgica alta."
                else:
                    texto_idade = f"Idade: {idade} anos (Risco Habitual).\nPredicao de via de parto: Fator sem risco adicional isolado. A literatura corrobora alta taxa de sucesso para evolucao de parto vaginal."
            
            texto_imc = "IMC nao calculado."
            if imc:
                if imc >= 30:
                    texto_imc = f"IMC: {imc:.1f} kg/m2 (Obesidade).\nPredicao de via de parto: A OMS alerta para maior risco de distocias, macrossomia fetal e falha na progressao. Aumenta substancialmente o risco basal de cesariana, embora a prova de trabalho de parto continue sendo recomendada."
                elif imc >= 25:
                    texto_imc = f"IMC: {imc:.1f} kg/m2 (Sobrepeso).\nPredicao de via de parto: Risco levemente aumentado para distocias de trajeto mole. Via vaginal continua sendo fortemente a via de eleicao."
                else:
                    texto_imc = f"IMC: {imc:.1f} kg/m2 (Eutrofia).\nPredicao de via de parto: Padrao de normalidade. Fator preditor altamente favoravel para o sucesso da resolucao por parto vaginal."

            comorbidades_list = []
            if hipertensao: comorbidades_list.append("Hipertensao Cronica")
            if diabetes_previa: comorbidades_list.append("Diabetes Pre-gestacional")
            if pre_eclampsia: comorbidades_list.append("Pre-eclampsia")
            if diabetes_gest: comorbidades_list.append("Diabetes Gestacional")
            if ciur: comorbidades_list.append("Restricao de Crescimento Fetal")
            if macrossomia: comorbidades_list.append("Macrossomia Fetal")
            if oligodramnio: comorbidades_list.append("Oligodramnio")
            if polidramnio: comorbidades_list.append("Polidramnio")
            
            texto_riscos = ""
            if placenta_previa:
                texto_riscos = "Fatores identificados (Gestacao de alto risco): Placenta Previa.\nPredicao de via de parto: Indicacao ABSOLUTA de cesariana. O parto vaginal esta contraindicado pelo risco hemorragico severo."
            elif len(comorbidades_list) > 0:
                texto_riscos = f"Fatores identificados (Gestacao de alto risco): {', '.join(comorbidades_list)}.\nPredicao de via de parto: Exigem monitoramento rigoroso intraparto e frequentemente indicam a necessidade de antecipacao do parto (inducao). Se o colo for desfavoravel, a taxa de cesariana nestes grupos e superior a da populacao de risco habitual."
            else:
                texto_riscos = "Fatores identificados: Nenhum fator de risco adicional detectado (Gestacao de Risco Habitual).\nPredicao de via de parto: Cenario extremamente favoravel para conducao de parto vaginal seguro."

            # --- 2. CÁLCULO DE ROBSON ---
            ig_robson = "Termo" if (dias_gest if dum else 280) >= 259 else "Pre-termo"
            paridade_total = partos_normais + partos_cesareos
            nulipara = (paridade_total == 0)
            multipara = (paridade_total > 0)
            tem_cesarea_previa = (partos_cesareos > 0)
            
            grupo_robson = "Indefinido"
            descricao_robson = ""
            repercussao_robson = ""

            if tipo_gestacao == "Múltiplo (Gêmeos ou mais)":
                grupo_robson = "Grupo 8"
                descricao_robson = "Todas as gestantes com gestacoes multiplas (incluindo cesarea previa)."
                repercussao_robson = "Alta taxa de cesariana, dependendo diretamente da apresentacao do primeiro feto e de protocolos institucionais."
            elif apresentacao in ["Córmica"] or situacao in ["Transversa", "Oblíqua"]:
                grupo_robson = "Grupo 9"
                descricao_robson = "Feto unico em situacao transversa ou obliqua."
                repercussao_robson = "Indicacao ABSOLUTA de cesariana na literatura atual. Via vaginal contraindicada."
            elif apresentacao == "Pélvica":
                if nulipara:
                    grupo_robson = "Grupo 6"
                    descricao_robson = "Nuliparas, feto unico, apresentacao pelvica."
                else:
                    grupo_robson = "Grupo 7"
                    descricao_robson = "Multiparas, feto unico, apresentacao pelvica."
                repercussao_robson = "A apresentacao pelvica esta fortemente associada a indicacao de cesariana eletiva na maioria dos servicos, salvo protocolos para Versao Cefalica Externa (VCE) bem-sucedida."
            elif ig_robson == "Pre-termo":
                grupo_robson = "Grupo 10"
                descricao_robson = "Feto unico, apresentacao cefalica, pre-termo (< 37 semanas)."
                repercussao_robson = "A via de parto prioritariamente recomendada e a vaginal. Contudo, devido a maior intolerancia fetal as contracoes (SFA), a taxa estatistica de resolucao por cesarea e elevada."
            else:
                if nulipara:
                    if inicio_tp == "Espontâneo":
                        grupo_robson = "Grupo 1"
                        descricao_robson = "Nuliparas, feto unico, cefalico, >= 37 semanas, TP espontaneo."
                        repercussao_robson = "Excelente prognostico. Espera-se alta taxa de sucesso para parto vaginal. O Ministerio da Saude orienta envidar esforcos para evitar a primeira cesarea neste grupo."
                    else:
                        grupo_robson = "Grupo 2"
                        descricao_robson = "Nuliparas, feto unico, cefalico, >= 37 semanas, induzido ou cesarea antes do TP."
                        repercussao_robson = "Risco substancialmente aumentado de cesarea em razao do processo de inducao em primigesta, especialmente se associado a colo uterino desfavoravel (baixo escore de Bishop)."
                elif multipara:
                    if tem_cesarea_previa:
                        grupo_robson = "Grupo 5"
                        descricao_robson = "Multiparas, feto unico, cefalico, >= 37 semanas, com cesarea(s) previa(s)."
                        repercussao_robson = "Candidatas classicas a prova de trabalho de parto (VBAC). O sucesso e viavel, porem, na pratica, este grupo concentra a maior parcela de cesarianas de repeticao nos hospitais."
                    else:
                        if inicio_tp == "Espontâneo":
                            grupo_robson = "Grupo 3"
                            descricao_robson = "Multiparas (sem cesarea previa), feto unico, cefalico, >= 37 semanas, TP espontaneo."
                            repercussao_robson = "Altissima probabilidade de parto vaginal rapido e bem-sucedido. O risco de cesarea neste cenario clinico e o menor de todos os grupos."
                        else:
                            grupo_robson = "Grupo 4"
                            descricao_robson = "Multiparas (sem cesarea previa), feto unico, cefalico, >= 37 semanas, induzido ou cesarea antes do TP."
                            repercussao_robson = "Excelente probabilidade de parto vaginal pela multiparidade, porem a necessidade de inducao eleva levemente o risco de falha comparado ao grupo 3."

            # --- 3. CÁLCULO DE BISHOP ---
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
            
            status_bishop = "Desfavoravel" if pontos_bishop <= 6 else "Favoravel"
            repercussao_bishop = "O colo maduro favorece amplamente a progressao natural ou uma eventual inducao, indicando alta probabilidade de desfecho vaginal com menor duracao de trabalho de parto." if status_bishop == "Favoravel" else "Colo imaturo. Maior risco de falha de inducao e evolucao para cesariana por parada de progressao. A literatura indica a necessidade de preparo cervical previo (ex: metodos mecanicos ou prostaglandinas)."

            # --- 4. AVALIAÇÃO VBAC ---
            texto_vbac = ""
            conclusao_vbac = ""
            
            if tem_cesarea_previa:
                fatores_vbac = []
                if vbac_previo: fatores_vbac.append("Historico de Parto Normal apos cesarea (Fator fortemente favoravel)")
                if motivo_cesarea_parada: fatores_vbac.append("Cesarea anterior por parada de progressao/descida (Fator desfavoravel)")
                if imc and imc >= 30: fatores_vbac.append("Obesidade - IMC >= 30 (Fator desfavoravel)")
                if idade and idade >= 35: fatores_vbac.append("Idade >= 35 anos (Fator desfavoravel)")
                
                if not fatores_vbac:
                    texto_vbac = "Nenhum fator preditor adverso ou positivo extremo identificado. O risco assume o padrao basal."
                    conclusao_vbac = "A paciente possui condicoes adequadas para a prova de trabalho de parto. A literatura indica taxas de sucesso (desfecho vaginal) entre 60% e 70%, o que desfavorece a indicacao de cesarea eletiva imediata de repeticao sem avaliacao do quadro agudo."
                else:
                    texto_vbac = " | ".join(fatores_vbac)
                    if vbac_previo:
                        conclusao_vbac = "predominancia de fator favoravel: O historico de VBAC previo eleva drasticamente a probabilidade estatistica de novo sucesso (>80%). A conduta pende firmemente para tentativa de via vaginal."
                    else:
                        conclusao_vbac = "presenca de fatores desfavoraveis: O cenario atual compromete o indice de sucesso basal calculado pelo modelo. Aumenta-se significativamente a chance real de que a tentativa de trabalho de parto culmine em nova cesariana."
            else:
                texto_vbac = "Nao aplicavel. Paciente sem historico de cesarea."
                conclusao_vbac = "Sem repercussao (avaliar via de parto pelos demais fatores)."

            # --- MONTAGEM DO RELATÓRIO FINAL ---
            nome_paciente = nome if nome else "Paciente nao identificada"
            data_atual = datetime.now().strftime("%d/%m/%Y as %H:%M")
            
            relatorio_final = f"""RELATÓRIO CLÍNICO DE APOIO À DECISÃO - CESASCORE
PACIENTE: {nome_paciente.upper()}

1. AVALIAÇÃO MATERNA E FATORES DE RISCO
{texto_idade}
{texto_imc}
{texto_riscos}

2. CLASSIFICAÇÃO DE ROBSON
(A Classificacao de Robson e padronizada pela OMS para categorizar gestantes, monitorar taxas de cesariana nos servicos e predizer a expectativa de via de parto.)
Identificado: {descricao_robson}
Classificação: {grupo_robson}
Repercussão na via de parto: {repercussao_robson}

3. ÍNDICE DE BISHOP
(O Indice de Bishop avalia clinicamente a maturidade cervical e prediz a probabilidade de sucesso de uma inducao do trabalho de parto ou da sua progressao espontanea.)
Identificado: Colo {status_bishop} (Pontuacao total: {pontos_bishop})
Repercussão na via de parto: {repercussao_bishop}

4. AVALIAÇÃO PARA VBAC (Parto Vaginal após Cesárea)
(O modelo matematico MFMU estima a probabilidade individualizada de sucesso de um parto normal apos uma cesarea, servindo para o aconselhamento obstetrico embasado.)
Identificado: {texto_vbac}
Repercussão na via de parto: {conclusao_vbac}
"""
            # Renderiza na Tela
            st.success("Relatório gerado com sucesso!")
            st.text_area("Cópia de Texto Rápido (Prontuário):", relatorio_final, height=500)
            
            # Gera PDF
            pdf_bytes = gerar_pdf(relatorio_final, data_atual)
            
            st.download_button(
                label="📥 Baixar Laudo Completo em PDF",
                data=pdf_bytes,
                file_name=f"CesaScore_Relatorio_{nome_paciente.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

# ==========================================
# COMANDO DE EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    main()
