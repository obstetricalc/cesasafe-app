import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta

# ==========================================
# FUNÇÃO DE CÁLCULO VBAC (Nova Versão IMC)
# ==========================================
def calcular_vbac(idade, peso_kg, altura_cm, hipertensao=False, 
                  parada_progressao=False, parto_vaginal_previo=False, vbac_previo=False):
    """
    Calculadora de Probabilidade de Sucesso do VBAC
    Baseada no modelo MFMU / Grobman 2021
    """
    # 1. Converter altura para metros
    altura_m = altura_cm / 100

    # 2. Calcular IMC
    imc = peso_kg / (altura_m ** 2)

    # 3. Converter variáveis booleanas
    hipertensao = int(hipertensao)
    parada_progressao = int(parada_progressao)
    parto_vaginal_previo = int(parto_vaginal_previo)
    vbac_previo = int(vbac_previo)

    # 4. Calcular escore linear (x)
    x = (
        3.302
        - (0.043 * idade)
        - (0.052 * imc)
        + (0.832 * parto_vaginal_previo)
        + (0.489 * vbac_previo)
        - (0.622 * parada_progressao)
        - (0.513 * hipertensao)
    )

    # 5. Aplicar função logística
    probabilidade = 1 / (1 + math.exp(-x))

    # 6. Converter para percentual
    percentual = probabilidade * 100

    # 7. Classificação opcional
    if percentual < 40:
        classificacao = "Baixa probabilidade"
    elif percentual < 60:
        classificacao = "Probabilidade intermediária"
    elif percentual < 80:
        classificacao = "Boa probabilidade"
    else:
        classificacao = "Alta probabilidade"

    # 8. Retorno
    return {
        "IMC": round(imc, 2),
        "Probabilidade_VBAC": round(percentual, 2),
        "Classificacao": classificacao
    }

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
    **Aviso Legal:** Esta ferramenta é um protótipo acadêmico auxiliar, baseado em protocolos assistenciais. 
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
        idade = st.number_input("Idade Materna (anos)", min_value=10, max_value=60, value=None, step=1, placeholder="Digite a idade")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 2: HISTÓRICO OBSTÉTRICO E DATAÇÃO
    # ==========================================
    st.header("2. Histórico Obstétrico")
    
    col_g, col_pn, col_pc, col_a = st.columns(4)
    with col_g:
        gestacoes = st.number_input("G (Gestações)", min_value=1, value=1)
    with col_pn:
        partos_normais = st.number_input("PN (Partos Normais)", min_value=0, value=0)
    with col_pc:
        partos_cesareos = st.number_input("PC (Partos Cesáreos)", min_value=0, value=0)
    with col_a:
        abortos = st.number_input("A (Abortos)", min_value=0, value=0)

    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com Parto Cesáreo Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo foi o último parto cesáreo?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("") 
    
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
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
        st.metric("DPP (pela DUM)", dpp_str)

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
        bcf = st.number_input("BCF (bpm)", min_value=0, max_value=250, value=140)
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
        dilatacao = st.selectbox("Dilatação (cm)", [0, 1, 2, 3], format_func=lambda x: ["0 cm", "1-2 cm", "3-4 cm", "≥ 5 cm"][x])
    with c2:
        apagamento = st.selectbox("Apagamento (%)", [0, 1, 2, 3], format_func=lambda x: ["0-30%", "40-50%", "60-70%", "≥ 80%"][x])
    with c3:
        altura = st.selectbox("Altura (De Lee)", [0, 1, 2, 3], format_func=lambda x: ["-3", "-2", "-1 ou 0", "+1 ou +2"][x])
    with c4:
        consistencia = st.selectbox("Consistência", [0, 1, 2], format_func=lambda x: ["Firme", "Média", "Amolecida"][x])
    with c5:
        posicao = st.selectbox("Posição", [0, 1, 2], format_func=lambda x: ["Posterior", "Média", "Anterior"][x])

    score_bishop = dilatacao + apagamento + altura + consistencia + posicao
    st.metric("Score de Bishop Total", f"{score_bishop}/13 pontos")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 5: PREDIÇÃO DE SUCESSO DO VBAC
    # ==========================================
    st.header("5. Predição de Sucesso do VBAC (TOLAC)")
    st.caption("Cálculo original MFMU (2021) aplicável a pacientes com parto cesáreo anterior.")

    resultado_vbac = None

    if partos_cesareos > 0:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            peso_vbac = st.number_input("Peso Pré-gestacional (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1, help="Insira o peso materno de antes do início da gestação atual.")
            altura_vbac = st.number_input("Altura Materna (cm)", min_value=100.0, max_value=220.0, value=160.0, step=1.0)
            hipertensao_vbac = st.checkbox("Paciente possui Hipertensão Crônica Tratada?")
            
        with col_v2:
            st.markdown("**Histórico Específico**")
            indicacao_parada = st.checkbox("O parto cesáreo anterior foi indicado por Parada de Progressão/Descida?")
            pv_previo_vbac = st.checkbox("Teve algum Parto Vaginal ANTES do primeiro parto cesáreo?")
            vbac_previo = st.checkbox("Já teve um VBAC (Parto Vaginal APÓS um parto cesáreo)?")

        if idade is not None:
            # Acionando a nova função
            resultado_vbac = calcular_vbac(
                idade=idade, 
                peso_kg=peso_vbac, 
                altura_cm=altura_vbac,
                hipertensao=hipertensao_vbac,
                parada_progressao=indicacao_parada, 
                parto_vaginal_previo=pv_previo_vbac,
                vbac_previo=vbac_previo
            )
            
            # Exibindo os resultados do dicionário de forma visualmente agradável
            st.success(f"📈 **Probabilidade Estimada de Sucesso (VBAC): {resultado_vbac['Probabilidade_VBAC']}%**")
            
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.info(f"📊 **Classificação:** {resultado_vbac['Classificacao']}")
            with c_res2:
                st.info(f"⚖️ **IMC Pré-gestacional:** {resultado_vbac['IMC']}")
                
        else:
            st.warning("⚠️ Preencha a 'Idade Materna' na Seção 1 (Identificação) para ativar o cálculo da MFMU.")
    else:
        st.info("💡 Calculadora não aplicável: A paciente não possui histórico de partos cesáreos.")

    st.markdown("---")

    # ==========================================
    # SEÇÃO 6: MALINAS
    # ==========================================
    st.header("6. Escore de Malinas")
    st.caption("Avaliação de risco para parto iminente (transporte).")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        m_paridade = st.selectbox("Paridade", [0, 1, 2], format_func=lambda x: ["1 parto", "2 partos", "≥3 partos"][x])
        m_duracao = st.selectbox("Duração do TP", [0, 1, 2], format_func=lambda x: ["< 3h", "3-5h", "> 6h"][x])
    with m2:
        m_membrana = st.selectbox("Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras", "Rotas <1h", "Rotas >1h"][x])
        m_distancia = st.selectbox("Dilatação/Descida", [0, 1, 2], format_func=lambda x: ["Alta/Fechada", "Média", "Baixa/Completa"][x])
    with m3:
        score_malinas = m_paridade + m_duracao + m_membrana + m_distancia
        st.metric("Score de Malinas", score_malinas)

    st.markdown("---")

    # ==========================================
    # SEÇÃO 7: CTG E RISCOS
    # ==========================================
    st.header("7. Avaliação Fetal e Fatores de Risco")
    col_fetal, col_indica = st.columns(2)

    with col_fetal:
        st.subheader("Cardiotocografia (CTG)")
        ctg_class = st.radio("Classificação NICHD", 
            ("Categoria I (Normal)", "Categoria II (Indeterminado)", "Categoria III (Anormal)"))
        liquido = st.selectbox("Aspecto do Líquido", ["Claro / Grumos Finos", "Meconial Fluido", "Meconial Espesso"])

    with col_indica:
        st.subheader("Indicações Clínicas")
        indicacoes_abs = st.multiselect("Fatores Presentes:", 
            ["Nenhum", "Placenta Prévia Total", "Iteratividade (2+ partos cesáreos)", 
             "Herpes Genital Ativo", "DCP", "Sofrimento Fetal Agudo", 
             "Pré-eclâmpsia Grave / Eclâmpsia"])

    # ==========================================
    # RELATÓRIO FINAL
    # ==========================================
    st.markdown("---")
    if st.button("GERAR PARECER CLÍNICO", type="primary"):
        analise_texto = []

        if idade is not None:
            if idade < 16: analise_texto.append(f"⚠️ **Idade ({idade}):** Adolescência precoce. Risco de DCP e síndromes hipertensivas.")
            elif idade >= 40: analise_texto.append(f"⚠️ **Idade ({idade}):** Risco aumentado para comorbidades e placentação anômala.")
        
        if bcf < 120 or bcf > 160:
            analise_texto.append(f"⚠️ **BCF Alterado ({bcf} bpm):** Investigar vitalidade fetal.")
        
        if score_bishop < 6:
            analise_texto.append(f"🔴 **Colo Desfavorável (Bishop {score_bishop}):** Se houver indicação, recomenda-se preparo cervical prévio.")
        else:
            analise_texto.append(f"🟢 **Colo Favorável (Bishop {score_bishop}):** Condições favoráveis à indução.")

        if partos_cesareos > 0:
            if tempo_cesarea == "Menos de 2 anos (< 24 meses)":
                analise_texto.append("⚠️ **Intervalo Curto:** Risco elevado de rotura uterina em prova de TP.")
            
            # Utilizando a variável dicionário resultado_vbac no relatório
            if resultado_vbac is not None:
                prob = resultado_vbac['Probabilidade_VBAC']
                classif = resultado_vbac['Classificacao']
                
                if prob >= 60.0:
                    analise_texto.append(f"🟢 **Predição VBAC ({prob}% - {classif}):** Probabilidade favorável para o TOLAC.")
                else:
                    analise_texto.append(f"🟡 **Predição VBAC ({prob}% - {classif}):** Probabilidade reduzida de sucesso. Reforçar aconselhamento sobre riscos versus benefícios.")

        if score_malinas >= 10:
            analise_texto.append("🔴 **ALERTA (Malinas ≥ 10):** Alto risco de parto no transporte.")
        
        if "Categoria III (Anormal)" in ctg_class or "Sofrimento Fetal Agudo" in indicacoes_abs:
            analise_texto.append("🚨 **EMERGÊNCIA:** Sinais de sofrimento fetal agudo. Indicação de extração imediata.")

        parecer_final = "\n\n".join(analise_texto)

        cor_box = "blue"
        if "EMERGÊNCIA" in parecer_final or "ALERTA" in parecer_final: cor_box = "red"
        elif "⚠️" in parecer_final or "🟡" in parecer_final: cor_box = "orange"
        else: cor_box = "green"

        st.markdown(f"""
        ### 🏥 Parecer Clínico Automatizado - CesaSafe
        **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
        **Identificação:** {nome if nome else 'Não identificada'}
        """)
        
        if cor_box == "red": st.error(parecer_final)
        elif cor_box == "orange": st.warning(parecer_final)
        elif cor_box == "green": st.success(parecer_final)
        else: st.info(parecer_final)

        st.text_area("Conduta Médica, Prescrição e Orientações", height=150)

if __name__ == "__main__":
    main()
