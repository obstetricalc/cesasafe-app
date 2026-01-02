import streamlit as st
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CesaSafe - ObstetriCalc", page_icon="🤰", layout="wide")

# --- FUNÇÃO: CLASSIFICAÇÃO DE ROBSON ---
def calcular_robson(paridade, cesareas, num_fetos, apresentacao, ig_semanas, inicio_trabalho):
    # Lógica simplificada dos 10 grupos de Robson
    # Paridade: 0 (Nulípara), 1+ (Multípara)
    
    if apresentacao != "Cefálica":
        if apresentacao == "Transversa/Oblíqua": return 9
        if apresentacao == "Pélvica":
            return 6 if paridade == 0 else 7

    if num_fetos > 1: return 8
    
    if ig_semanas < 37: return 10
    
    if cesareas > 0: return 5

    # A partir daqui: Cefálico, Único, >=37s, Sem cesárea prévia
    if paridade == 0: # Nulípara
        if inicio_trabalho == "Espontâneo": return 1
        else: return 2 # Induzido ou Cesárea antes do TP
    else: # Multípara
        if inicio_trabalho == "Espontâneo": return 3
        else: return 4 # Induzido ou Cesárea antes do TP

# --- APP PRINCIPAL ---
def main():
    # Menu Lateral
    with st.sidebar:
        st.title("🤰 CesaSafe")
        st.info("**Ferramenta de Apoio à Decisão Obstétrica**")
        st.markdown("---")
        st.write("Desenvolvido por:")
        st.write("**Juliana da Costa Furtado**")
        st.write("*Mestranda CIPE/UEPA*")
        st.markdown("---")
        modo_impressao = st.checkbox("🖨️ Modo de Impressão (Ocultar menus)")

    # Cabeçalho
    if not modo_impressao:
        st.title("Relatório Clínico Obstétrico")
        st.markdown("Preencha os dados abaixo para gerar os escores de Bishop, Malinas e Classificação de Robson.")
    else:
        st.markdown("## 🏥 Relatório CesaSafe")
        st.markdown(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    st.markdown("---")

    # --- 1. DADOS DA PACIENTE ---
    st.subheader("1. Identificação e Obstetrícia")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        nome = st.text_input("Nome da Gestante")
        idade = st.number_input("Idade", 12, 50, 25)
    with col2:
        ig = st.number_input("IG (Semanas)", 20, 45, 39)
        num_fetos = st.selectbox("Nº Fetos", [1, 2, 3], format_func=lambda x: "Único" if x==1 else "Múltiplo")
    with col3:
        paridade_n = st.number_input("Paridade (Partos Anteriores)", 0, 10, 0)
        cesareas = st.number_input("Cesáreas Anteriores", 0, 10, 0)
    with col4:
        apresentacao = st.selectbox("Apresentação", ["Cefálica", "Pélvica", "Transversa/Oblíqua"])
        inicio_tp = st.selectbox("Início do Trabalho de Parto", ["Espontâneo", "Induzido", "Cesárea Antes do TP"])

    # --- 2. BISHOP ---
    st.markdown("---")
    st.subheader("2. Índice de Bishop (Maturação Cervical)")
    
    b1, b2, b3, b4, b5 = st.columns(5)
    dilatacao = b1.selectbox("Dilatação", [0, 1, 2, 3], format_func=lambda x: ["0 cm (0)", "1-2 cm (1)", "3-4 cm (2)", "≥5 cm (3)"][x])
    apagamento = b2.selectbox("Apagamento", [0, 1, 2, 3], format_func=lambda x: ["0-30% (0)", "40-50% (1)", "60-70% (2)", "≥80% (3)"][x])
    altura = b3.selectbox("Altura (De Lee)", [0, 1, 2, 3], format_func=lambda x: ["-3 (0)", "-2 (1)", "-1, 0 (2)", "+1, +2 (3)"][x])
    consistencia = b4.selectbox("Consistência", [0, 1, 2], format_func=lambda x: ["Firme (0)", "Média (1)", "Mole (2)"][x])
    posicao = b5.selectbox("Posição", [0, 1, 2], format_func=lambda x: ["Posterior (0)", "Média (1)", "Anterior (2)"][x])
    
    score_bishop = dilatacao + apagamento + altura + consistencia + posicao

    # --- 3. MALINAS ---
    st.markdown("---")
    st.subheader("3. Escore de Malinas (Iminência de Parto)")
    m1, m2, m3, m4 = st.columns(4)
    
    mal_paridade = m1.selectbox("Paridade (Malinas)", [0, 1, 2], format_func=lambda x: ["1 parto (0)", "2 partos (1)", "≥3 partos (2)"][x])
    mal_tempo = m2.selectbox("Duração do TP", [0, 1, 2], format_func=lambda x: ["<3h (0)", "3-5h (1)", ">6h (2)"][x])
    mal_memb = m3.selectbox("Membranas", [0, 1, 2], format_func=lambda x: ["Íntegras (0)", "Rotas recente (1)", "Rotas >1h (2)"][x])
    mal_desc = m4.selectbox("Distância/Descida", [0, 1, 2], format_func=lambda x: ["Alta (0)", "Média (1)", "Baixa (2)"][x])
    
    score_malinas = mal_paridade + mal_tempo + mal_memb + mal_desc

    # --- 4. PROCESSAMENTO ---
    robson_group = calcular_robson(paridade_n, cesareas, num_fetos, apresentacao, ig, inicio_tp)

    # Lógica de Cor e Mensagem do Robson
    robson_msg = ""
    if robson_group in [1, 2, 3, 4]:
        robson_msg = "Grupos de Baixo Risco para Cesárea (Idealmente)"
    elif robson_group == 5:
        robson_msg = "Cesárea Prévia (Avaliar Prova de Trabalho de Parto)"
    else:
        robson_msg = "Situações Especiais / Alto Risco de Cesárea"

    # --- 5. RESULTADOS ---
    st.markdown("---")
    if not modo_impressao:
        st.markdown("### 📊 Resultados Consolidados")
    
    c_res1, c_res2, c_res3 = st.columns(3)
    
    with c_res1:
        st.info(f"**Robson: Grupo {robson_group}**")
        st.caption(robson_msg)
    
    with c_res2:
        cor_b = "green" if score_bishop >= 6 else "orange"
        st.markdown(f":{cor_b}[**Bishop: {score_bishop}**]")
        st.caption("Favorável" if score_bishop >= 6 else "Desfavorável (Indução difícil)")

    with c_res3:
        cor_m = "red" if score_malinas >= 10 else ("orange" if score_malinas >= 5 else "green")
        st.markdown(f":{cor_m}[**Malinas: {score_malinas}**]")
        if score_malinas < 5: st.caption("Sem iminência")
        elif score_malinas < 10: st.caption("Parto possível no transporte")
        else: st.caption("🚨 PARTO IMINENTE")

    # --- ÁREA DE CONDUTA ---
    st.markdown("### 📝 Conduta e Observações")
    st.text_area("Descreva a conduta (ex: Internação, Indução, Cesárea, Alta)", height=100)
    
    if modo_impressao:
        st.markdown("---")
        st.caption("Documento gerado pelo sistema CesaSafe - Uso Acadêmico/Profissional")
    else:
        st.warning("⚠️ Para imprimir: Marque 'Modo de Impressão' no menu lateral e use o atalho Ctrl+P do navegador.")

if __name__ == "__main__":
    main()
