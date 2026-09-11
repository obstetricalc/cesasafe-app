import streamlit as st
from datetime import datetime, date, timedelta, timezone
from uuid import uuid4
from fpdf import FPDF


# =========================================================
# CONFIGURAÇÃO GERAL
# =========================================================
st.set_page_config(
    page_title="CESASCORE: Predição da Via de Parto",
    layout="wide",
)

FUSO_BRASILIA = timezone(timedelta(hours=-3))
HOJE_BRASILIA = datetime.now(FUSO_BRASILIA).date()

AVISO_LEGAL = (
    "Ferramenta acadêmica de apoio baseada em protocolos assistenciais. "
    "A decisão clínica final é de responsabilidade do médico obstetra."
)


# =========================================================
# FUNÇÕES UTILITÁRIAS
# =========================================================
def gerar_codigo_identificacao():
    if "codigo_identificacao" not in st.session_state:
        prefixo = datetime.now(FUSO_BRASILIA).strftime("%Y%m%d")
        sufixo = uuid4().hex[:8].upper()
        st.session_state["codigo_identificacao"] = f"CESA-{prefixo}-{sufixo}"
    return st.session_state["codigo_identificacao"]


def calcular_idade(data_nasc):
    if not data_nasc:
        return None
    return (
        HOJE_BRASILIA.year
        - data_nasc.year
        - ((HOJE_BRASILIA.month, HOJE_BRASILIA.day) < (data_nasc.month, data_nasc.day))
    )


def calcular_imc(peso_kg, altura_m):
    if peso_kg is None or altura_m is None or altura_m <= 0:
        return None
    return peso_kg / (altura_m ** 2)


def calcular_ig_por_dum(dum):
    if not dum:
        return None
    dias = (HOJE_BRASILIA - dum).days
    if dias < 0:
        return None
    return {
        "dias": dias,
        "semanas": dias // 7,
        "dias_restantes": dias % 7,
        "dpp": dum + timedelta(days=280),
    }


def calcular_ig_por_dpp_eco(dpp_eco):
    if not dpp_eco:
        return None
    # Fórmula descrita no documento-base:
    # IGeco (dias) = 280 - número de dias entre a avaliação e a DPPeco.
    dias_ate_dpp = (dpp_eco - HOJE_BRASILIA).days
    dias_gestacao = 280 - dias_ate_dpp
    if dias_gestacao < 0:
        return None
    return {
        "dias": dias_gestacao,
        "semanas": dias_gestacao // 7,
        "dias_restantes": dias_gestacao % 7,
    }


def formatar_data(valor):
    return valor.strftime("%d/%m/%Y") if valor else "Não informado"


def formatar_ig(ig):
    if not ig:
        return "Não informada"
    return f"{ig['semanas']} semanas e {ig['dias_restantes']} dias"


def sim_nao(valor):
    if valor is None:
        return "Não informado"
    return valor


# =========================================================
# INTERPRETAÇÕES — IDENTIFICAÇÃO
# =========================================================
def analisar_idade(idade):
    if idade is None:
        return "Idade materna: não informada."

    if idade <= 14:
        return (
            "Idade materna: ≤14 anos\n"
            "Interpretação: idade materna muito jovem, associada a maior atenção e risco obstétrico.\n"
            "Peso na análise: fator de atenção obstétrica, devendo ser interpretado conjuntamente com os demais "
            "dados maternos e obstétricos. Isoladamente, não constitui indicação de parto cesáreo."
        )

    if 15 <= idade <= 34:
        return (
            "Idade materna: 15–34 anos\n"
            "Interpretação: faixa etária sem fator de risco adicional relacionado à idade para a predição de parto cesáreo.\n"
            "Peso na análise: risco habitual relacionado à idade, devendo ser interpretado conjuntamente com os demais "
            "dados obstétricos e clínicos."
        )

    return (
        "Idade materna: ≥35 anos\n"
        "Interpretação: idade materna avançada, associada a maior probabilidade de parto cesáreo.\n"
        "Peso na análise: fator associado, devendo ser interpretado conjuntamente com os demais dados obstétricos e clínicos. "
        "Isoladamente, não constitui indicação obrigatória de parto cesáreo."
    )


def analisar_imc(imc):
    if imc is None:
        return "IMC pré-gestacional: não calculado por ausência de peso e/ou altura."

    if imc < 18.5:
        return (
            f"IMC pré-gestacional: {imc:.1f} kg/m²\n"
            "Interpretação: baixo peso.\n"
            "Peso na análise: não está associado, de forma consistente, ao aumento da probabilidade de cesariana."
        )

    if imc < 25:
        return (
            f"IMC pré-gestacional: {imc:.1f} kg/m²\n"
            "Interpretação: peso adequado.\n"
            "Peso na análise: faixa de menor probabilidade de cesariana. Não garante parto vaginal, pois a via de parto "
            "depende dos demais fatores obstétricos."
        )

    if imc < 30:
        return (
            f"IMC pré-gestacional: {imc:.1f} kg/m²\n"
            "Interpretação: sobrepeso.\n"
            "Peso na análise: fator associado ao aumento da probabilidade de cesariana, sem constituir indicação isolada "
            "para o procedimento."
        )

    return (
        f"IMC pré-gestacional: {imc:.1f} kg/m²\n"
        "Interpretação: obesidade.\n"
        "Peso na análise: fator associado ao aumento da probabilidade de cesariana, sem constituir indicação isolada "
        "para o procedimento."
    )


def analisar_medicacoes(medicacoes, anticoagulante_12h):
    if not medicacoes:
        return (
            "Sem uso de medicações contínuas\n"
            "Interpretação: ausência de tratamento farmacológico contínuo informado.\n"
            "Peso na análise: neutro para a predição da via de parto. A ausência de medicação contínua não modifica, "
            "isoladamente, a probabilidade de cesariana."
        )

    textos = []

    if "Anticoagulantes" in medicacoes:
        texto = (
            "Anticoagulantes\n"
            "Interpretação: uso associado principalmente ao aumento do risco hemorrágico.\n"
            "Peso na análise: não aumenta, isoladamente, a probabilidade de cesariana, mas representa fator de atenção "
            "para segurança materna caso haja necessidade de parto operatório."
        )
        if anticoagulante_12h == "Sim":
            texto += "\nATENÇÃO: anticoagulante utilizado nas últimas 12 horas — sinalizar alto risco de sangramento."
        elif anticoagulante_12h == "Não":
            texto += "\nAnticoagulante nas últimas 12 horas: não."
        else:
            texto += "\nAnticoagulante nas últimas 12 horas: não informado."
        textos.append(texto)

    if "Anti-hipertensivos" in medicacoes:
        textos.append(
            "Anti-hipertensivos\n"
            "Interpretação: podem indicar presença de hipertensão arterial crônica ou síndrome hipertensiva da gestação.\n"
            "Peso na análise: fator indireto para predição da via de parto. O uso do medicamento, isoladamente, não prediz "
            "cesariana; a relevância depende da condição hipertensiva, do controle pressórico, da presença de lesão de órgão-alvo "
            "e de sinais de insuficiência placentária."
        )

    if "Insulina ou Hipoglicemiantes orais" in medicacoes:
        textos.append(
            "Insulina ou hipoglicemiantes orais\n"
            "Interpretação: sugerem presença de diabetes pré-gestacional ou diabetes gestacional em tratamento farmacológico.\n"
            "Peso na análise: fator indireto. A medicação não deve elevar automaticamente a probabilidade de cesariana; "
            "a análise deve considerar a condição metabólica materna e suas repercussões obstétricas, especialmente quando "
            "associadas a alterações fetais."
        )

    if "Anticonvulsivantes" in medicacoes:
        textos.append(
            "Anticonvulsivantes\n"
            "Interpretação: podem estar relacionados ao tratamento de epilepsia ou outras condições neurológicas maternas.\n"
            "Peso na análise: fator indireto. O uso isolado não constitui preditor de cesariana. A relevância para a via de parto "
            "depende da doença de base, do controle clínico e da existência de repercussões maternas ou fetais."
        )

    if "Imunossupressores" in medicacoes:
        textos.append(
            "Imunossupressores\n"
            "Interpretação: indicam, em geral, condição autoimune, inflamatória ou situação clínica que exija imunossupressão.\n"
            "Peso na análise: fator indireto. O medicamento isoladamente não aumenta a probabilidade de cesariana; a análise "
            "deve considerar a doença de base e suas repercussões maternas e obstétricas."
        )

    if "Corticoides prolongados" in medicacoes:
        textos.append(
            "Corticoides prolongados\n"
            "Interpretação: podem indicar doença inflamatória, autoimune ou outra condição materna crônica em tratamento prolongado.\n"
            "Peso na análise: fator indireto. O uso prolongado de corticoide, isoladamente, não determina maior probabilidade de "
            "parto cesáreo. Sua relevância depende da condição clínica associada e do estado materno."
        )

    return "\n\n".join(textos)


# =========================================================
# INTERPRETAÇÕES — HISTÓRICO OBSTÉTRICO
# =========================================================
def analisar_paridade(partos_normais, partos_cesareos):
    total_partos = (partos_normais or 0) + (partos_cesareos or 0)

    if 1 <= total_partos <= 4:
        return (
            f"Partos prévios: {total_partos}\n"
            "Interpretação: condição obstétrica de risco habitual.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras condições maternas, fetais ou obstétricas "
            "que indiquem cesariana."
        )

    if total_partos > 4:
        return (
            f"Partos prévios: {total_partos}\n"
            "Interpretação: alto risco de sangramento.\n"
            "Peso na análise: neutro para a predição da via de parto; não aumenta, isoladamente, a probabilidade de cesariana. "
            "Alerta, entretanto, para alto risco de sangramento. A via vaginal permanece possível na ausência de outras "
            "indicações obstétricas para cesárea."
        )

    return "Partos prévios: nenhum."


def analisar_partos_vaginais(partos_normais, partos_cesareos):
    partos_normais = partos_normais or 0
    partos_cesareos = partos_cesareos or 0

    if partos_normais == 0:
        return (
            "Nenhum parto vaginal prévio\n"
            "Interpretação: ausência de antecedente de parto vaginal.\n"
            "Peso na análise: neutro a menos favorável à via vaginal, especialmente na presença de cesárea prévia; "
            "não constitui indicação de cesariana."
        )

    texto = (
        "≥1 parto vaginal prévio\n"
        "Interpretação: antecedente obstétrico favorável ao parto vaginal.\n"
        "Peso na análise: favorável à via vaginal e associado a maior probabilidade de novo parto vaginal, inclusive em "
        "mulheres com cesárea prévia. O Ministério da Saúde considera o parto vaginal prévio fortemente relacionado ao "
        "sucesso do parto vaginal após cesariana."
    )
    return texto


def analisar_cesareas_previas(partos_cesareos, intervalo_ultima_cesarea):
    partos_cesareos = partos_cesareos or 0

    if partos_cesareos == 0:
        return "Partos cesáreos prévios: nenhum."

    if partos_cesareos == 1:
        texto = (
            "1 cesárea prévia\n"
            "Interpretação: presença de uma cicatriz uterina prévia.\n"
            "Peso na análise: fator de atenção, mas compatível com parto vaginal. Na ausência de contraindicações, recomenda-se "
            "considerar e encorajar tentativa de parto vaginal. O sucesso descrito é elevado."
        )
    elif partos_cesareos == 2:
        texto = (
            "2 cesáreas prévias\n"
            "Interpretação: maior risco relacionado à cicatriz uterina, especialmente ruptura uterina.\n"
            "Peso na análise: aumenta a relevância da cesariana na decisão da via de parto, porém a conduta deve ser individualizada; "
            "parto vaginal ainda pode ser considerado em casos selecionados."
        )
    else:
        texto = (
            "≥3 cesáreas prévias\n"
            "Interpretação: múltiplas cicatrizes uterinas, com aumento do risco de ruptura uterina durante tentativa de parto vaginal.\n"
            "Peso na análise: fortemente favorável à cesariana. O Ministério da Saúde recomenda operação cesariana em mulheres "
            "com três ou mais cesáreas prévias."
        )

    if intervalo_ultima_cesarea == "Menos de 2 anos":
        texto += (
            "\nATENÇÃO: último parto cesáreo há menos de 2 anos — condição fortemente favorável à cesariana devido ao risco de ruptura uterina."
        )

    return texto


def analisar_comorbidades(comorbidades):
    if not comorbidades:
        return "Comorbidades/condições obstétricas selecionadas: nenhuma."

    textos = []

    if "Pré-eclâmpsia" in comorbidades:
        textos.append(
            "Pré-eclâmpsia\n"
            "Interpretação: síndrome hipertensiva da gestação, com gravidade variável.\n"
            "Peso na análise: favorável à via vaginal quando houver condições maternas e fetais adequadas. A pré-eclâmpsia, "
            "isoladamente, não constitui indicação de cesariana; esta deve ser reservada às indicações obstétricas ou situações "
            "em que as condições materno-fetais exijam resolução mais rápida."
        )

    if "Diabetes Gestacional" in comorbidades:
        textos.append(
            "Diabetes gestacional\n"
            "Interpretação: hiperglicemia diagnosticada durante a gestação, podendo estar associada principalmente a crescimento fetal excessivo.\n"
            "Peso na análise: neutro isoladamente para a via de parto. O diabetes gestacional não constitui indicação de cesariana; "
            "a decisão deve considerar principalmente peso fetal estimado, controle glicêmico, vitalidade fetal e demais condições obstétricas."
        )

    if "Placenta Prévia" in comorbidades:
        textos.append(
            "Placenta prévia\n"
            "Interpretação: implantação placentária no segmento uterino inferior, cuja relação com o orifício cervical interno determina a via de parto.\n"
            "Peso na análise: fortemente favorável à cesariana quando centro-total ou centro-parcial. A cesariana programada é "
            "recomendada nessas situações. Placenta de inserção baixa não deve ser interpretada automaticamente da mesma forma."
        )

    if "Gestação Gemelar" in comorbidades:
        textos.append(
            "Gestação gemelar\n"
            "Interpretação: gestação com dois fetos; a via de parto depende principalmente da apresentação do primeiro gemelar "
            "e das características da gestação.\n"
            "Peso na análise: se o primeiro feto for cefálico, a via de parto deve ser individualizada e o parto vaginal é possível. "
            "Se o primeiro feto for não cefálico, a cesariana é recomendada. Gestação monoamniótica também apresenta indicação "
            "de cesariana programada."
        )

    if "Restrição de Crescimento Fetal" in comorbidades:
        textos.append(
            "Restrição de crescimento fetal (RCF)\n"
            "Interpretação: crescimento fetal abaixo do esperado, cuja gravidade depende principalmente da vitalidade fetal e da função placentária.\n"
            "Peso na análise: neutro/condicional para a via de parto."
        )

    if "Macrossomia Fetal" in comorbidades:
        textos.append(
            "Macrossomia fetal\n"
            "Interpretação: crescimento fetal excessivo, associado a maior risco de distócia de ombro e complicações no parto.\n"
            "Peso na análise: associada a maior probabilidade de cesariana conforme aumenta o peso fetal estimado, mas a suspeita "
            "de macrossomia isoladamente não determina cesárea. A FEBRASGO considera especialmente relevante a cesariana planejada "
            "quando o peso fetal estimado é >4.500 g em gestantes diabéticas ou >5.000 g em gestantes não diabéticas."
        )

    if "Oligodrâmnio" in comorbidades:
        textos.append(
            "Oligodrâmnio\n"
            "Interpretação: redução do volume de líquido amniótico, cuja importância depende da causa, idade gestacional e vitalidade fetal.\n"
            "Peso na análise: neutro/condicional para a via de parto."
        )

    if "Polidrâmnio" in comorbidades:
        textos.append(
            "Polidrâmnio\n"
            "Interpretação: aumento excessivo do volume de líquido amniótico, associado a maior ocorrência de apresentações fetais anômalas "
            "e outras complicações obstétricas.\n"
            "Peso na análise: neutro/condicional para a via de parto."
        )

    return "\n\n".join(textos)


# =========================================================
# INTERPRETAÇÕES — EXAME FÍSICO E OBSTÉTRICO
# =========================================================
def analisar_numero_fetos(numero_fetos, apresentacao):
    if numero_fetos is None:
        return "Número de fetos: não informado."

    if numero_fetos == "Único":
        return (
            "Feto único\n"
            "Interpretação: gestação única.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras condições maternas, fetais ou obstétricas que indiquem cesariana."
        )

    if numero_fetos == "Gemelar (2 fetos)":
        complemento = ""
        if apresentacao == "Cefálica":
            complemento = " O primeiro feto foi informado como cefálico, condição em que a via vaginal pode ser considerada."
        elif apresentacao in {"Pélvica", "Córmica"}:
            complemento = " O primeiro feto foi informado como não cefálico, situação em que o documento-base recomenda cesariana."
        return (
            "Gestação gemelar\n"
            "Interpretação: gestação múltipla, com maior complexidade obstétrica.\n"
            "Peso na análise: associada a maior probabilidade de cesariana, porém a via de parto depende principalmente da apresentação "
            "do primeiro feto e das características da gestação. Se o primeiro feto for cefálico, a via vaginal pode ser considerada; "
            "se for não cefálico, a cesariana é recomendada." + complemento
        )

    return (
        "≥3 fetos\n"
        "Interpretação: gestação múltipla de maior complexidade.\n"
        "Peso na análise: fortemente associado à via cesariana, devido ao maior risco materno-fetal e à complexidade do parto."
    )


def analisar_situacao_fetal(situacao):
    if situacao is None:
        return "Situação fetal: não informada."

    if situacao == "Longitudinal":
        return (
            "Situação fetal longitudinal\n"
            "Interpretação: eixo fetal paralelo ao eixo materno.\n"
            "Peso na análise: favorável à via vaginal, especialmente quando associada à apresentação cefálica."
        )

    if situacao == "Transversa":
        return (
            "Situação fetal transversa\n"
            "Interpretação: eixo fetal perpendicular ao eixo materno.\n"
            "Peso na análise: fortemente favorável à cesariana quando persistente, pois impossibilita o parto vaginal espontâneo."
        )

    return (
        "Situação fetal oblíqua\n"
        "Interpretação: eixo fetal em posição intermediária entre longitudinal e transversa.\n"
        "Peso na análise: aumenta a probabilidade de cesariana se persistente no momento do parto, devendo ser reavaliada, pois pode evoluir "
        "para situação longitudinal."
    )


def analisar_apresentacao_fetal(apresentacao):
    if apresentacao is None:
        return "Apresentação fetal: não informada."

    if apresentacao == "Cefálica":
        return (
            "Apresentação cefálica\n"
            "Interpretação: polo cefálico apresentado ao canal de parto.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras contraindicações obstétricas."
        )

    if apresentacao == "Pélvica":
        return (
            "Apresentação pélvica\n"
            "Interpretação: pelve ou membros inferiores apresentados ao canal de parto.\n"
            "Peso na análise: associada a maior probabilidade de cesariana. O parto vaginal pode ser considerado em situações selecionadas, "
            "com equipe experiente e critérios adequados; portanto, não constitui indicação absoluta de cesárea em todos os casos."
        )

    return (
        "Apresentação córmica/ombro\n"
        "Interpretação: apresentação geralmente associada à situação transversa.\n"
        "Peso na análise: fortemente favorável à cesariana quando persistente no trabalho de parto, por incompatibilidade com o parto vaginal espontâneo."
    )


def analisar_inicio_tp(inicio_tp):
    if inicio_tp is None:
        return "Início do trabalho de parto: não informado."

    if inicio_tp == "Espontâneo":
        return (
            "Trabalho de parto espontâneo\n"
            "Interpretação: trabalho de parto iniciado espontaneamente.\n"
            "Peso na análise: favorável à via vaginal, quando há evolução adequada e ausência de outras indicações de cesariana."
        )

    if inicio_tp == "Induzido":
        return (
            "Trabalho de parto induzido\n"
            "Interpretação: trabalho de parto iniciado por intervenção farmacológica ou mecânica.\n"
            "Peso na análise: fator de atenção para a predição da via de parto. Não constitui indicação de cesariana; o desfecho depende "
            "principalmente da indicação da indução, condições cervicais, resposta uterina e evolução do trabalho de parto."
        )

    return (
        "Cesárea antes do trabalho de parto / sem trabalho de parto\n"
        "Interpretação: ausência de trabalho de parto no momento da avaliação.\n"
        "Peso na análise: neutro isoladamente. A via de parto depende das demais condições obstétricas."
    )


def analisar_bcf(bcf):
    if bcf is None:
        return "Batimentos cardíacos fetais: não informados."

    if bcf < 120:
        return (
            f"BCF: {bcf} bpm\n"
            "Interpretação: bradicardia fetal; quando persistente, pode indicar comprometimento fetal.\n"
            "Peso na análise: aumenta a probabilidade de necessidade de resolução operatória, especialmente se persistente e não responsiva "
            "às medidas corretivas. A cesariana pode ser necessária quando o parto vaginal não é iminente."
        )

    # O documento-base traz um intervalo tipográfico "120–120 bpm". Para não deixar
    # 121–159 bpm sem classificação e manter coerência com o corte seguinte (≥160),
    # utiliza-se 120–159 bpm como faixa basal sem alerta.
    if 120 <= bcf < 160:
        return (
            f"BCF: {bcf} bpm\n"
            "Interpretação: faixa basal sem critério de alerta.\n"
            "Peso na análise: favorável à manutenção da via vaginal, desde que não existam desacelerações ou outros sinais de comprometimento fetal."
        )

    return (
        f"BCF: {bcf} bpm\n"
        "Interpretação: taquicardia fetal e sinal de alerta, devendo ser investigada a causa.\n"
        "Peso na análise: fator de atenção; isoladamente não determina cesariana, mas alterações persistentes associadas a outros sinais "
        "de comprometimento fetal aumentam a probabilidade de resolução operatória."
    )


def analisar_contracoes(contracoes):
    if contracoes is None:
        return "Contrações uterinas: não informadas."

    if 3 <= contracoes <= 5:
        return (
            f"Contrações uterinas: {contracoes}/10 min\n"
            "Interpretação: frequência uterina considerada adequada durante o trabalho de parto.\n"
            "Peso na análise: favorável à evolução da via vaginal, quando acompanhada de progressão cervical e bem-estar fetal."
        )

    if contracoes <= 2:
        return (
            f"Contrações uterinas: {contracoes}/10 min\n"
            "Interpretação: atividade uterina possivelmente insuficiente.\n"
            "Peso na análise: pode reduzir a probabilidade de progressão vaginal se persistente, mas não constitui indicação isolada de cesariana; "
            "deve ser interpretada juntamente com dilatação cervical e evolução do trabalho de parto."
        )

    return (
        f"Contrações uterinas: {contracoes}/10 min\n"
        "Interpretação: atividade uterina excessiva/taquissistolia, com risco de comprometimento fetal.\n"
        "Peso na análise: fator de alerta. Não determina isoladamente cesariana, mas, se persistente e associada a alteração da frequência "
        "cardíaca fetal, aumenta a probabilidade de necessidade de resolução operatória."
    )


def analisar_inspecao(herpes, sangramento, prolapso):
    textos = []

    if herpes == "Sim":
        textos.append(
            "Herpes genital ativo\n"
            "Interpretação: presença de lesões genitais compatíveis com herpes no momento do trabalho de parto.\n"
            "Peso na análise: fortemente favorável à cesariana, devido ao risco de transmissão neonatal."
        )
    elif herpes == "Não":
        textos.append(
            "Sem lesão herpética genital ativa\n"
            "Interpretação: ausência de lesões genitais ativas e de sintomas prodrômicos no momento do parto.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras indicações obstétricas para cesariana."
        )
    else:
        textos.append("Herpes genital ativo: não informado.")

    if sangramento == "Sim":
        textos.append(
            "Com sangramento vaginal intenso\n"
            "Interpretação: sinal de alerta para hemorragia obstétrica, podendo estar relacionado a placenta prévia, descolamento prematuro "
            "de placenta, vasa prévia ou outras causas.\n"
            "Peso na análise: aumenta a probabilidade de cesariana, especialmente quando associado a comprometimento materno ou fetal. "
            "A causa do sangramento deve ser investigada."
        )
    elif sangramento == "Não":
        textos.append(
            "Sem sangramento vaginal intenso\n"
            "Interpretação: ausência de sinal hemorrágico importante no momento da avaliação.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras condições maternas, fetais ou obstétricas que indiquem cesariana."
        )
    else:
        textos.append("Sangramento vaginal intenso: não informado.")

    if prolapso == "Sim":
        textos.append(
            "Com prolapso de cordão\n"
            "Interpretação: emergência obstétrica com risco de compressão do cordão e comprometimento fetal.\n"
            "Peso na análise: fortemente favorável à cesariana de emergência, quando o parto vaginal imediato não é possível."
        )
    elif prolapso == "Não":
        textos.append(
            "Sem prolapso de cordão\n"
            "Interpretação: ausência de descida do cordão umbilical à frente da apresentação fetal.\n"
            "Peso na análise: favorável à via vaginal, na ausência de outras indicações obstétricas para cesariana."
        )
    else:
        textos.append("Prolapso de cordão: não informado.")

    return "\n\n".join(textos)


# =========================================================
# ÍNDICE DE BISHOP
# =========================================================
def calcular_bishop(dilatacao, esvaecimento, altura_apres, consistencia, posicao_colo):
    if None in [dilatacao, esvaecimento, altura_apres, consistencia, posicao_colo]:
        return None

    pontos = 0

    pontos_dilatacao = {
        "Fechado": 0,
        "1 a 2 cm": 1,
        "3 a 4 cm": 2,
        "5 cm ou mais": 3,
    }
    pontos_esvaecimento = {
        "0 a 30%": 0,
        "40 a 50%": 1,
        "60 a 70%": 2,
        "80% ou mais": 3,
    }
    pontos_altura = {
        "-3": 0,
        "-2": 1,
        "-1": 2,
        "0": 2,
        "+1": 3,
        "+2": 3,
        "+3": 3,
    }
    pontos_consistencia = {
        "Firme": 0,
        "Médio": 1,
        "Amolecido": 2,
    }
    pontos_posicao = {
        "Posterior": 0,
        "Centralizado": 1,
        "Anterior": 2,
    }

    pontos += pontos_dilatacao[dilatacao]
    pontos += pontos_esvaecimento[esvaecimento]
    pontos += pontos_altura[altura_apres]
    pontos += pontos_consistencia[consistencia]
    pontos += pontos_posicao[posicao_colo]

    if pontos <= 5:
        classificacao = "Colo desfavorável à indução"
        interpretacao = (
            "Interpretação: colo desfavorável à indução.\n"
            "Peso na análise: menor probabilidade de sucesso da indução e de parto vaginal, com maior possibilidade de cesariana por falha "
            "de indução. Não constitui, isoladamente, indicação de cesárea."
        )
    elif pontos <= 7:
        classificacao = "Condições cervicais intermediárias"
        interpretacao = (
            "Interpretação: condições cervicais intermediárias.\n"
            "Peso na análise: probabilidade intermediária de sucesso da indução e parto vaginal. Deve ser analisado conjuntamente com paridade, "
            "apresentação fetal, idade gestacional e demais condições obstétricas."
        )
    else:
        classificacao = "Colo favorável/maduro"
        interpretacao = (
            "Interpretação: colo favorável/maduro.\n"
            "Peso na análise: favorável à indução e ao parto vaginal, associado a maior probabilidade de sucesso da indução e menor probabilidade "
            "de cesariana por falha de indução."
        )

    return {
        "pontos": pontos,
        "classificacao": classificacao,
        "interpretacao": interpretacao,
    }


# =========================================================
# CLASSIFICAÇÃO DE ROBSON
# =========================================================
def classificar_robson(partos_normais, partos_cesareos, numero_fetos, situacao, apresentacao, inicio_tp, ig_dias):
    if numero_fetos is None or situacao is None or apresentacao is None or inicio_tp is None or ig_dias is None:
        return {
            "grupo": "Indefinido",
            "interpretacao": "Dados insuficientes para classificação automática de Robson.",
            "peso": "Preencher idade gestacional de referência, número de fetos, situação, apresentação e início do trabalho de parto.",
        }

    total_partos = (partos_normais or 0) + (partos_cesareos or 0)
    nulipara = total_partos == 0
    tem_cesarea_previa = (partos_cesareos or 0) > 0
    termo = ig_dias >= 259

    if numero_fetos != "Único":
        return {
            "grupo": "Grupo 8",
            "interpretacao": "gestação múltipla, com ou sem cesárea prévia.",
            "peso": "associado a maior probabilidade de cesariana, dependendo principalmente da apresentação fetal, número de fetos e antecedentes obstétricos.",
        }

    if situacao in {"Transversa", "Oblíqua"} or apresentacao == "Córmica":
        return {
            "grupo": "Grupo 9",
            "interpretacao": "situação fetal transversa ou oblíqua, com ou sem cesárea prévia.",
            "peso": "fortemente favorável à cesariana quando a situação anômala persiste no momento do parto, por inviabilizar o parto vaginal espontâneo.",
        }

    if apresentacao == "Pélvica":
        if nulipara:
            return {
                "grupo": "Grupo 6",
                "interpretacao": "nulípara, feto único, apresentação pélvica.",
                "peso": "associado a maior probabilidade de cesariana, devido à apresentação pélvica.",
            }
        return {
            "grupo": "Grupo 7",
            "interpretacao": "multípara, feto único, apresentação pélvica, com ou sem cesárea prévia.",
            "peso": "associado a maior probabilidade de cesariana, devendo ser considerado em conjunto com os antecedentes obstétricos.",
        }

    if apresentacao != "Cefálica":
        return {
            "grupo": "Indefinido",
            "interpretacao": "Apresentação fetal não compatível com os critérios disponíveis para classificação automática neste fluxo.",
            "peso": "Revisar situação e apresentação fetal.",
        }

    if not termo:
        return {
            "grupo": "Grupo 10",
            "interpretacao": "feto único, cefálico, <37 semanas, com ou sem cesárea prévia.",
            "peso": "variável para a predição da via de parto. A prematuridade, isoladamente, não determina cesariana; a via depende das condições maternas, fetais e obstétricas.",
        }

    if tem_cesarea_previa:
        return {
            "grupo": "Grupo 5",
            "interpretacao": "multípara com pelo menos uma cesárea prévia, feto único, cefálico, ≥37 semanas.",
            "peso": "associado a maior probabilidade de cesariana, principalmente pela presença de cicatriz uterina prévia. Não constitui, isoladamente, indicação de nova cesárea.",
        }

    if nulipara:
        if inicio_tp == "Espontâneo":
            return {
                "grupo": "Grupo 1",
                "interpretacao": "nulípara, feto único, cefálico, ≥37 semanas, trabalho de parto espontâneo.",
                "peso": "favorável à via vaginal, por reunir características obstétricas de menor complexidade e trabalho de parto espontâneo.",
            }
        return {
            "grupo": "Grupo 2",
            "interpretacao": "nulípara, feto único, cefálico, ≥37 semanas, com indução ou cesárea antes do trabalho de parto.",
            "peso": "maior probabilidade de cesariana em relação ao Grupo 1. Na indução, o parto vaginal permanece possível; na cesariana antes do trabalho de parto, a via já está definida.",
        }

    if inicio_tp == "Espontâneo":
        return {
            "grupo": "Grupo 3",
            "interpretacao": "multípara sem cesárea prévia, feto único, cefálico, ≥37 semanas, trabalho de parto espontâneo.",
            "peso": "fortemente favorável à via vaginal, especialmente pela multiparidade, ausência de cesárea prévia e início espontâneo do trabalho de parto.",
        }

    return {
        "grupo": "Grupo 4",
        "interpretacao": "multípara sem cesárea prévia, feto único, cefálico, ≥37 semanas, com indução ou cesárea antes do trabalho de parto.",
        "peso": "favorabilidade intermediária à via vaginal quando submetida à indução. Na cesariana antes do trabalho de parto, a via já está definida.",
    }


# =========================================================
# GERAÇÃO DO RELATÓRIO
# =========================================================
def montar_relatorio(dados):
    idade = calcular_idade(dados["data_nasc"])
    imc = calcular_imc(dados["peso_pre_kg"], dados["altura_m"])
    ig_dum = calcular_ig_por_dum(dados["dum"])
    ig_eco = calcular_ig_por_dpp_eco(dados["dpp_eco"])

    if dados["ig_referencia"] == "DUM":
        ig_ref = ig_dum
        fonte_ig = "DUM"
    elif dados["ig_referencia"] == "1ª USG":
        ig_ref = ig_eco
        fonte_ig = "1ª USG (DPPeco)"
    else:
        ig_ref = None
        fonte_ig = "Não definida"

    bishop = calcular_bishop(
        dados["dilatacao"],
        dados["esvaecimento"],
        dados["altura_apres"],
        dados["consistencia"],
        dados["posicao_colo"],
    )

    robson = classificar_robson(
        dados["partos_normais"],
        dados["partos_cesareos"],
        dados["numero_fetos"],
        dados["situacao"],
        dados["apresentacao"],
        dados["inicio_tp"],
        ig_ref["dias"] if ig_ref else None,
    )

    meds_str = ", ".join(dados["medicacoes"]) if dados["medicacoes"] else "Nenhuma"
    comorb_str = ", ".join(dados["comorbidades"]) if dados["comorbidades"] else "Nenhuma"

    dpp_dum_str = formatar_data(ig_dum["dpp"]) if ig_dum else "Não calculada"
    ig_dum_str = formatar_ig(ig_dum)
    ig_eco_str = formatar_ig(ig_eco)

    bishop_resumo = (
        f"{bishop['pontos']} pontos — {bishop['classificacao']}"
        if bishop
        else "Não calculado por ausência de um ou mais componentes do toque vaginal"
    )

    data_hora = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y às %H:%M")

    texto = f"""RELATÓRIO CLÍNICO DE APOIO À DECISÃO - CESASCORE
CÓDIGO DE IDENTIFICAÇÃO: {dados['codigo_identificacao']}

DADOS INFORMADOS

Data de nascimento: {formatar_data(dados['data_nasc'])}
Idade: {idade if idade is not None else 'Não informada'}
Peso pré-gestacional: {f"{dados['peso_pre_kg']:.1f} kg" if dados['peso_pre_kg'] is not None else 'Não informado'}
Altura: {f"{dados['altura_m']:.2f} m" if dados['altura_m'] is not None else 'Não informada'}
IMC pré-gestacional: {f"{imc:.1f} kg/m²" if imc is not None else 'Não calculado'}
Medicações de uso contínuo: {meds_str}
Anticoagulante nas últimas 12 horas: {sim_nao(dados['anticoagulante_12h']) if 'Anticoagulantes' in dados['medicacoes'] else 'Não se aplica'}

Histórico obstétrico: G{dados['gestacoes']} PN{dados['partos_normais']} PC{dados['partos_cesareos']} A{dados['abortos']}
Intervalo desde a última cesárea: {dados['intervalo_ultima_cesarea'] if dados['partos_cesareos'] > 0 else 'Não se aplica'}
DUM: {formatar_data(dados['dum'])}
DPP pela DUM: {dpp_dum_str}
IG pela DUM: {ig_dum_str}
DPP pela 1ª USG (DPPeco): {formatar_data(dados['dpp_eco'])}
IG pela 1ª USG: {ig_eco_str}
IG utilizada para análise: {fonte_ig} — {formatar_ig(ig_ref)}
Comorbidades/condições obstétricas: {comorb_str}

Número de fetos: {dados['numero_fetos'] or 'Não informado'}
Situação fetal: {dados['situacao'] or 'Não informada'}
Apresentação fetal: {dados['apresentacao'] or 'Não informada'}
Início do trabalho de parto: {dados['inicio_tp'] or 'Não informado'}
Altura uterina: {str(dados['au']) + ' cm' if dados['au'] is not None else 'Não informada'}
BCF: {str(dados['bcf']) + ' bpm' if dados['bcf'] is not None else 'Não informado'}
Contrações uterinas: {str(dados['contracoes']) + '/10 min' if dados['contracoes'] is not None else 'Não informadas'}
Herpes genital ativo: {sim_nao(dados['herpes'])}
Sangramento vaginal intenso: {sim_nao(dados['sangramento'])}
Prolapso de cordão: {sim_nao(dados['prolapso'])}

Toque vaginal: Dilatação {dados['dilatacao'] or 'N/I'} | Esvaecimento {dados['esvaecimento'] or 'N/I'} | De Lee {dados['altura_apres'] or 'N/I'} | Consistência {dados['consistencia'] or 'N/I'} | Posição {dados['posicao_colo'] or 'N/I'}
Proporção céfalo-pélvica: {dados['proporcao_cefalo_pelvica'] or 'Não informada'}
Índice de Bishop: {bishop_resumo}
Classificação de Robson: {robson['grupo']}

________________________________________________________________________________

ANÁLISE DOS DADOS – CESASCORE

1. IDENTIFICAÇÃO

1.1 IDADE
{analisar_idade(idade)}

1.2 IMC PRÉ-GESTACIONAL
{analisar_imc(imc)}

1.3 MEDICAÇÕES EM USO
{analisar_medicacoes(dados['medicacoes'], dados['anticoagulante_12h'])}

________________________________________________________________________________

2. HISTÓRICO OBSTÉTRICO

2.1 GESTAÇÕES / PARIDADE
{analisar_paridade(dados['partos_normais'], dados['partos_cesareos'])}

2.2 PARTOS VAGINAIS PRÉVIOS
{analisar_partos_vaginais(dados['partos_normais'], dados['partos_cesareos'])}

2.3 PARTOS CESÁREOS PRÉVIOS
{analisar_cesareas_previas(dados['partos_cesareos'], dados['intervalo_ultima_cesarea'])}

2.4 IDADE GESTACIONAL
DUM: {formatar_data(dados['dum'])}
DPP calculada pela DUM: {dpp_dum_str}
IG calculada pela DUM: {ig_dum_str}
DPPeco: {formatar_data(dados['dpp_eco'])}
IGeco calculada: {ig_eco_str}
Referência selecionada para a análise: {fonte_ig} — {formatar_ig(ig_ref)}

2.5 COMORBIDADES MATERNAS / CONDIÇÕES OBSTÉTRICAS
{analisar_comorbidades(dados['comorbidades'])}

________________________________________________________________________________

3. EXAME FÍSICO E OBSTÉTRICO

3.1 AVALIAÇÃO FETAL

NÚMERO DE FETOS
{analisar_numero_fetos(dados['numero_fetos'], dados['apresentacao'])}

SITUAÇÃO FETAL
{analisar_situacao_fetal(dados['situacao'])}

APRESENTAÇÃO FETAL
{analisar_apresentacao_fetal(dados['apresentacao'])}

INÍCIO DO TRABALHO DE PARTO
{analisar_inicio_tp(dados['inicio_tp'])}

BATIMENTOS CARDÍACOS FETAIS
{analisar_bcf(dados['bcf'])}

CONTRAÇÕES UTERINAS
{analisar_contracoes(dados['contracoes'])}

3.2 INSPEÇÃO
{analisar_inspecao(dados['herpes'], dados['sangramento'], dados['prolapso'])}

3.3 PROPORÇÃO CÉFALO-PÉLVICA
Proporção céfalo-pélvica informada: {dados['proporcao_cefalo_pelvica'] or 'Não informada'}.

________________________________________________________________________________

4. ÍNDICE DE BISHOP
"""

    if bishop:
        texto += f"""
Pontuação total: {bishop['pontos']} pontos.
Classificação: {bishop['classificacao']}.
{bishop['interpretacao']}
"""
    else:
        texto += "\nÍndice não calculado por ausência de um ou mais componentes do toque vaginal.\n"

    texto += f"""

________________________________________________________________________________

5. CLASSIFICAÇÃO DE ROBSON

Classificação: {robson['grupo']}
Interpretação: {robson['interpretacao']}
Peso na análise: {robson['peso']}

________________________________________________________________________________

Aviso Legal: {AVISO_LEGAL}
Relatório gerado em: {data_hora}
Profissional avaliador: {dados['profissional_avaliador'] if dados['profissional_avaliador'] else '________________________________________'}
"""

    return texto, data_hora


# =========================================================
# PDF
# =========================================================
class PDF(FPDF):
    def footer(self):
        self.set_y(-25)
        try:
            self.image("1.jpg", 72, self.get_y(), 16)
            self.image("2.png", 97, self.get_y(), 16)
            self.image("3.png", 122, self.get_y(), 16)
        except Exception:
            pass


def gerar_pdf(relatorio_texto):
    pdf = PDF()
    pdf.set_auto_page_break(True, margin=35)
    pdf.add_page()

    try:
        pdf.image("logo.png", 75, 8, 60)
        pdf.set_y(45)
    except Exception:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "CESASCORE - RELATÓRIO", 0, 1, "C")
        pdf.ln(8)

    texto_latin = relatorio_texto.encode("latin-1", "replace").decode("latin-1")

    bold_triggers = [
        "DADOS INFORMADOS",
        "ANÁLISE DOS DADOS",
        "1. IDENTIFICAÇÃO",
        "2. HISTÓRICO OBSTÉTRICO",
        "3. EXAME FÍSICO E OBSTÉTRICO",
        "4. ÍNDICE DE BISHOP",
        "5. CLASSIFICAÇÃO DE ROBSON",
        "1.1 IDADE",
        "1.2 IMC",
        "1.3 MEDICAÇÕES",
        "2.1 GESTAÇÕES",
        "2.2 PARTOS VAGINAIS",
        "2.3 PARTOS CESÁREOS",
        "2.4 IDADE GESTACIONAL",
        "2.5 COMORBIDADES",
        "3.1 AVALIAÇÃO FETAL",
        "3.2 INSPEÇÃO",
        "3.3 PROPORÇÃO CÉFALO-PÉLVICA",
        "NÚMERO DE FETOS",
        "SITUAÇÃO FETAL",
        "APRESENTAÇÃO FETAL",
        "INÍCIO DO TRABALHO DE PARTO",
        "BATIMENTOS CARDÍACOS FETAIS",
        "CONTRAÇÕES UTERINAS",
    ]

    inline_labels = [
        "Interpretação:",
        "Peso na análise:",
        "Classificação:",
        "Pontuação total:",
        "Aviso Legal:",
        "Relatório gerado em:",
        "Profissional avaliador:",
    ]

    for linha in texto_latin.split("\n"):
        linha_limpa = linha.strip()

        if not linha_limpa:
            pdf.ln(3)
            continue

        if linha_limpa.startswith("RELATÓRIO CLÍNICO"):
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(190, 7, linha_limpa, 0, "C")
            continue

        if linha_limpa.startswith("CÓDIGO DE IDENTIFICAÇÃO:"):
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(190, 6, linha_limpa, 0, "C")
            pdf.ln(4)
            continue

        if linha_limpa.startswith("____"):
            pdf.ln(2)
            pdf.set_draw_color(220, 220, 220)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
            continue

        if any(linha_limpa.startswith(trigger) for trigger in bold_triggers):
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(190, 6, linha, 0, "L")
            continue

        foi_inline = False
        for label in inline_labels:
            if linha_limpa.startswith(label):
                partes = linha.split(":", 1)
                pdf.set_font("Arial", "B", 9)
                pdf.write(5, partes[0] + ":")
                pdf.set_font("Arial", "", 9)
                restante = partes[1] if len(partes) > 1 else ""
                pdf.write(5, restante + "\n")
                foi_inline = True
                break

        if not foi_inline:
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(190, 5, linha, 0, "L")

    saida = pdf.output(dest="S")
    if isinstance(saida, str):
        return saida.encode("latin-1")
    return bytes(saida)


# =========================================================
# CONFIRMAÇÃO DOS DADOS
# =========================================================
def montar_resumo_confirmacao(dados):
    idade = calcular_idade(dados["data_nasc"])
    imc = calcular_imc(dados["peso_pre_kg"], dados["altura_m"])
    ig_dum = calcular_ig_por_dum(dados["dum"])
    ig_eco = calcular_ig_por_dpp_eco(dados["dpp_eco"])

    return f"""
**Código de identificação:** {dados['codigo_identificacao']}  
**Data de nascimento:** {formatar_data(dados['data_nasc'])} — **Idade:** {idade if idade is not None else 'N/I'}  
**Peso pré-gestacional:** {f"{dados['peso_pre_kg']:.1f} kg" if dados['peso_pre_kg'] is not None else 'N/I'} — **Altura:** {f"{dados['altura_m']:.2f} m" if dados['altura_m'] is not None else 'N/I'} — **IMC:** {f"{imc:.1f} kg/m²" if imc is not None else 'N/I'}  
**Medicações:** {', '.join(dados['medicacoes']) if dados['medicacoes'] else 'Nenhuma'}  
**Histórico obstétrico:** G{dados['gestacoes']} PN{dados['partos_normais']} PC{dados['partos_cesareos']} A{dados['abortos']}  
**DUM:** {formatar_data(dados['dum'])} — **IG DUM:** {formatar_ig(ig_dum)}  
**DPPeco:** {formatar_data(dados['dpp_eco'])} — **IGeco:** {formatar_ig(ig_eco)}  
**IG de referência:** {dados['ig_referencia'] or 'Não definida'}  
**Comorbidades/condições obstétricas:** {', '.join(dados['comorbidades']) if dados['comorbidades'] else 'Nenhuma'}  
**Fetos / Situação / Apresentação:** {dados['numero_fetos'] or 'N/I'} / {dados['situacao'] or 'N/I'} / {dados['apresentacao'] or 'N/I'}  
**Início do TP:** {dados['inicio_tp'] or 'N/I'}  
**AU / BCF / Contrações:** {str(dados['au']) + ' cm' if dados['au'] is not None else 'N/I'} / {str(dados['bcf']) + ' bpm' if dados['bcf'] is not None else 'N/I'} / {str(dados['contracoes']) + '/10 min' if dados['contracoes'] is not None else 'N/I'}  
**Inspeção — Herpes / Sangramento intenso / Prolapso de cordão:** {sim_nao(dados['herpes'])} / {sim_nao(dados['sangramento'])} / {sim_nao(dados['prolapso'])}  
**Toque vaginal:** Dilatação {dados['dilatacao'] or 'N/I'}; Esvaecimento {dados['esvaecimento'] or 'N/I'}; De Lee {dados['altura_apres'] or 'N/I'}; Consistência {dados['consistencia'] or 'N/I'}; Posição {dados['posicao_colo'] or 'N/I'}  
**Proporção céfalo-pélvica:** {dados['proporcao_cefalo_pelvica'] or 'N/I'}  
**Profissional avaliador:** {dados['profissional_avaliador'] or 'Não informado'}
"""


def conteudo_confirmacao():
    dados = st.session_state.get("snapshot_pendente")
    if not dados:
        st.warning("Não há dados pendentes para confirmação.")
        return

    st.markdown("Confira cuidadosamente os dados antes de gerar o relatório.")
    st.markdown(montar_resumo_confirmacao(dados))

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmar e gerar relatório", type="primary", use_container_width=True):
            st.session_state["snapshot_relatorio"] = dados.copy()
            st.session_state["relatorio_confirmado"] = True
            st.session_state["snapshot_pendente"] = None
            st.rerun()
    with c2:
        if st.button("Voltar e revisar dados", use_container_width=True):
            st.session_state["snapshot_pendente"] = None
            st.rerun()


if hasattr(st, "dialog"):
    mostrar_confirmacao = st.dialog("CONFIRMAÇÃO DE DADOS", width="large")(conteudo_confirmacao)
else:
    mostrar_confirmacao = conteudo_confirmacao


# =========================================================
# APLICAÇÃO PRINCIPAL
# =========================================================
def main():
    st.markdown(
        """
        <style>
            [data-testid="InputInstructions"] { display: none !important; visibility: hidden !important; }
            p, span, label, input, select, textarea, li, div[data-testid="stMarkdownContainer"] p {
                font-size: 20px !important;
            }
            h1 { font-size: 3.2rem !important; }
            h2 { font-size: 2.6rem !important; }
            h3 { font-size: 2.0rem !important; color: #1A6B7C !important; }
            .block-container { padding-top: 1.5rem !important; }
            .stApp { background-color: #F8FAFC !important; }
            [data-testid="stHeader"] { background-color: transparent !important; }
            h1, h2, h4 { color: #0B3B60 !important; font-weight: 600 !important; }
            div[data-testid="stImage"] {
                display: flex !important;
                justify-content: center !important;
                text-align: center !important;
                margin: 0 auto !important;
                width: 100% !important;
            }
            div[data-testid="stImage"] > img {
                width: 650px !important;
                max-width: 100% !important;
                height: auto !important;
                margin: 0 auto !important;
            }
            .stButton > button[kind="primary"] {
                background-color: #1A6B7C !important;
                color: white !important;
                border-radius: 8px !important;
                border: none !important;
                font-weight: bold !important;
                font-size: 19px !important;
            }
            .stButton > button[kind="primary"]:hover {
                background-color: #124B57 !important;
            }
            div[data-testid="stMetricValue"] { color: #1A6B7C !important; font-size: 34px !important; }
            div[data-testid="stExpander"] {
                border-radius: 12px !important;
                border: 1px solid #F1F5F9 !important;
                background-color: #FFFFFF !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
                margin-bottom: 1.5rem !important;
            }
            div[data-testid="stExpander"] summary p {
                font-size: 1.8rem !important;
                color: #0B3B60 !important;
                font-weight: 600 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_espaco_esq, col_logo, col_espaco_dir = st.columns([1, 2, 1])
    with col_logo:
        try:
            st.image("logo.png", use_container_width=True)
        except Exception:
            st.markdown(
                "<h1 style='text-align:center;color:#0B3B60;'>CESASCORE</h1>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"<p style='font-size:16px !important;'><b>Aviso Legal:</b> {AVISO_LEGAL}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    codigo_identificacao = gerar_codigo_identificacao()

    # =====================================================
    # 1. IDENTIFICAÇÃO
    # =====================================================
    with st.expander("1. IDENTIFICAÇÃO", expanded=False):
        st.text_input(
            "**Código de Identificação**",
            value=codigo_identificacao,
            disabled=True,
            help="Gerado automaticamente pelo sistema.",
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            data_nasc = st.date_input(
                "**Data de Nascimento**",
                value=None,
                min_value=date(HOJE_BRASILIA.year - 60, 1, 1),
                max_value=HOJE_BRASILIA,
                format="DD/MM/YYYY",
            )
        with c2:
            idade = calcular_idade(data_nasc)
            st.metric("Idade", f"{idade} anos" if idade is not None else "—")
        with c3:
            peso_pre_kg = st.number_input(
                "**Peso pré-gestacional (kg)**",
                min_value=30.0,
                max_value=250.0,
                value=None,
                step=0.1,
                format="%.1f",
            )

        c4, c5 = st.columns(2)
        with c4:
            altura_m = st.number_input(
                "**Altura (m)**",
                min_value=1.00,
                max_value=2.50,
                value=None,
                step=0.01,
                format="%.2f",
            )
        with c5:
            imc = calcular_imc(peso_pre_kg, altura_m)
            st.metric("IMC pré-gestacional", f"{imc:.1f} kg/m²" if imc is not None else "—")

        st.markdown("---")
        st.markdown("### Medicações de Uso Contínuo")
        medicacoes = st.multiselect(
            "Selecione uma ou mais opções, quando aplicável:",
            options=[
                "Anticoagulantes",
                "Anti-hipertensivos",
                "Insulina ou Hipoglicemiantes orais",
                "Anticonvulsivantes",
                "Imunossupressores",
                "Corticoides prolongados",
            ],
        )

        anticoagulante_12h = None
        if "Anticoagulantes" in medicacoes:
            anticoagulante_12h = st.radio(
                "**Anticoagulante utilizado nas últimas 12 horas?**",
                options=["Sim", "Não"],
                index=None,
                horizontal=True,
            )
            if anticoagulante_12h == "Sim":
                st.error("ATENÇÃO: sinalizar alto risco de sangramento.")

    # =====================================================
    # 2. HISTÓRICO OBSTÉTRICO
    # =====================================================
    with st.expander("2. HISTÓRICO OBSTÉTRICO", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            gestacoes = st.number_input("**G (Gestações)**", min_value=1, value=1, step=1)
        with c2:
            partos_normais = st.number_input("**PN (Partos Normais)**", min_value=0, value=0, step=1)
        with c3:
            partos_cesareos = st.number_input("**PC (Partos Cesáreos)**", min_value=0, value=0, step=1)
        with c4:
            abortos = st.number_input("**A (Abortos)**", min_value=0, value=0, step=1)

        intervalo_ultima_cesarea = None
        if partos_cesareos > 0:
            intervalo_ultima_cesarea = st.radio(
                "**Há quanto tempo ocorreu o último parto cesáreo?**",
                options=["Menos de 2 anos", "2 anos ou mais"],
                index=None,
                horizontal=True,
            )

        st.markdown("---")
        c5, c6, c7 = st.columns(3)
        with c5:
            dum = st.date_input(
                "**Data da Última Menstruação (DUM)**",
                value=None,
                max_value=HOJE_BRASILIA,
                format="DD/MM/YYYY",
            )
        with c6:
            ig_dum = calcular_ig_por_dum(dum)
            st.metric("IG pela DUM", formatar_ig(ig_dum) if ig_dum else "—")
        with c7:
            st.metric("DPP pela DUM", formatar_data(ig_dum["dpp"]) if ig_dum else "—")

        c8, c9 = st.columns(2)
        with c8:
            dpp_eco = st.date_input(
                "**Data Provável do Parto pela 1ª USG (DPPeco)**",
                value=None,
                format="DD/MM/YYYY",
            )
        with c9:
            ig_eco = calcular_ig_por_dpp_eco(dpp_eco)
            st.metric("IG pela 1ª USG", formatar_ig(ig_eco) if ig_eco else "—")

        if ig_dum and ig_eco:
            ig_referencia = st.radio(
                "**Qual idade gestacional o sistema deverá utilizar para gerar a análise dos resultados?**",
                options=["DUM", "1ª USG"],
                index=None,
                horizontal=True,
            )
        elif ig_dum:
            ig_referencia = "DUM"
            st.info("Para a análise, será utilizada a idade gestacional calculada pela DUM.")
        elif ig_eco:
            ig_referencia = "1ª USG"
            st.info("Para a análise, será utilizada a idade gestacional calculada pela 1ª USG.")
        else:
            ig_referencia = None

        if ig_dum and not (0 <= ig_dum["dias"] <= 315):
            st.warning("A idade gestacional calculada pela DUM está fora da faixa usual de 0 a 45 semanas. Revise a data informada.")
        if ig_eco and not (0 <= ig_eco["dias"] <= 315):
            st.warning("A idade gestacional calculada pela DPPeco está fora da faixa usual de 0 a 45 semanas. Revise a data informada.")

        st.markdown("---")
        st.markdown("### Comorbidades Maternas / Condições Obstétricas")
        comorbidades = st.multiselect(
            "Selecione uma ou mais opções, quando aplicável:",
            options=[
                "Pré-eclâmpsia",
                "Diabetes Gestacional",
                "Placenta Prévia",
                "Gestação Gemelar",
                "Restrição de Crescimento Fetal",
                "Macrossomia Fetal",
                "Oligodrâmnio",
                "Polidrâmnio",
            ],
        )

    # =====================================================
    # 3. EXAME FÍSICO E OBSTÉTRICO
    # =====================================================
    with st.expander("3. EXAME FÍSICO E OBSTÉTRICO", expanded=False):
        st.subheader("Avaliação Fetal")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            numero_fetos = st.selectbox(
                "**Número de fetos**",
                options=["Único", "Gemelar (2 fetos)", "3 ou mais fetos"],
                index=None,
                placeholder="Selecione...",
            )
        with c2:
            situacao = st.selectbox(
                "**Situação fetal**",
                options=["Longitudinal", "Transversa", "Oblíqua"],
                index=None,
                placeholder="Selecione...",
            )
        with c3:
            apresentacao = st.selectbox(
                "**Apresentação fetal / do 1º feto**",
                options=["Cefálica", "Pélvica", "Córmica"],
                index=None,
                placeholder="Selecione...",
            )
        with c4:
            inicio_tp = st.selectbox(
                "**Início do trabalho de parto**",
                options=["Espontâneo", "Induzido", "Cesárea antes do trabalho de parto"],
                index=None,
                placeholder="Selecione...",
            )

        c5, c6, c7 = st.columns(3)
        with c5:
            au = st.number_input(
                "**Altura uterina (AU cm)**",
                min_value=0,
                max_value=60,
                value=None,
                step=1,
            )
        with c6:
            bcf = st.number_input(
                "**Batimentos Cardiofetais (BCF bpm)**",
                min_value=0,
                max_value=250,
                value=None,
                step=1,
            )
        with c7:
            contracoes = st.number_input(
                "**Contrações / 10 min**",
                min_value=0,
                max_value=10,
                value=None,
                step=1,
            )

        st.markdown("---")
        st.subheader("Inspeção")
        c8, c9, c10 = st.columns(3)
        with c8:
            herpes = st.radio(
                "**Herpes genital ativo**",
                options=["Sim", "Não"],
                index=None,
                horizontal=True,
            )
        with c9:
            sangramento = st.radio(
                "**Sangramento vaginal intenso**",
                options=["Sim", "Não"],
                index=None,
                horizontal=True,
            )
        with c10:
            prolapso = st.radio(
                "**Prolapso de cordão**",
                options=["Sim", "Não"],
                index=None,
                horizontal=True,
            )

        st.markdown("---")
        st.subheader("Toque Vaginal")

        c11, c12, c13 = st.columns(3)
        with c11:
            dilatacao = st.selectbox(
                "**Dilatação (cm)**",
                options=["Fechado", "1 a 2 cm", "3 a 4 cm", "5 cm ou mais"],
                index=None,
                placeholder="Selecione...",
            )
        with c12:
            esvaecimento = st.selectbox(
                "**Esvaecimento (%)**",
                options=["0 a 30%", "40 a 50%", "60 a 70%", "80% ou mais"],
                index=None,
                placeholder="Selecione...",
            )
        with c13:
            altura_apres = st.selectbox(
                "**Altura da apresentação (De Lee)**",
                options=["-3", "-2", "-1", "0", "+1", "+2", "+3"],
                index=None,
                placeholder="Selecione...",
            )

        c14, c15, c16 = st.columns(3)
        with c14:
            consistencia = st.selectbox(
                "**Consistência do colo**",
                options=["Firme", "Médio", "Amolecido"],
                index=None,
                placeholder="Selecione...",
            )
        with c15:
            posicao_colo = st.selectbox(
                "**Posição do colo**",
                options=["Posterior", "Centralizado", "Anterior"],
                index=None,
                placeholder="Selecione...",
            )
        with c16:
            proporcao_cefalo_pelvica = st.selectbox(
                "**Proporção Céfalo-Pélvica**",
                options=["Adequado", "Desproporção céfalo-pélvica"],
                index=None,
                placeholder="Selecione...",
            )

        bishop_preview = calcular_bishop(
            dilatacao,
            esvaecimento,
            altura_apres,
            consistencia,
            posicao_colo,
        )
        if bishop_preview:
            st.info(
                f"Índice de Bishop calculado automaticamente: {bishop_preview['pontos']} pontos — "
                f"{bishop_preview['classificacao']}."
            )

    # =====================================================
    # 4. RELATÓRIO CESASCORE
    # =====================================================
    with st.expander("4. RELATÓRIO CESASCORE", expanded=False):
        profissional_avaliador = st.text_input(
            "**Profissional avaliador**",
            placeholder="Digite o nome do profissional responsável pela avaliação",
        )

        dados_atuais = {
            "codigo_identificacao": codigo_identificacao,
            "data_nasc": data_nasc,
            "peso_pre_kg": peso_pre_kg,
            "altura_m": altura_m,
            "medicacoes": medicacoes,
            "anticoagulante_12h": anticoagulante_12h,
            "gestacoes": int(gestacoes),
            "partos_normais": int(partos_normais),
            "partos_cesareos": int(partos_cesareos),
            "abortos": int(abortos),
            "intervalo_ultima_cesarea": intervalo_ultima_cesarea,
            "dum": dum,
            "dpp_eco": dpp_eco,
            "ig_referencia": ig_referencia,
            "comorbidades": comorbidades,
            "numero_fetos": numero_fetos,
            "situacao": situacao,
            "apresentacao": apresentacao,
            "inicio_tp": inicio_tp,
            "au": au,
            "bcf": bcf,
            "contracoes": contracoes,
            "herpes": herpes,
            "sangramento": sangramento,
            "prolapso": prolapso,
            "dilatacao": dilatacao,
            "esvaecimento": esvaecimento,
            "altura_apres": altura_apres,
            "consistencia": consistencia,
            "posicao_colo": posicao_colo,
            "proporcao_cefalo_pelvica": proporcao_cefalo_pelvica,
            "profissional_avaliador": profissional_avaliador,
        }

        if st.button("Gerar Relatório", type="primary", use_container_width=True):
            if ig_dum and ig_eco and ig_referencia is None:
                st.error("Selecione qual idade gestacional deverá ser utilizada na análise: DUM ou 1ª USG.")
            else:
                st.session_state["snapshot_pendente"] = dados_atuais.copy()
                mostrar_confirmacao()

        if st.session_state.get("relatorio_confirmado") and st.session_state.get("snapshot_relatorio"):
            relatorio_final, _ = montar_relatorio(st.session_state["snapshot_relatorio"])
            st.success("Relatório CESASCORE gerado com sucesso.")
            st.text_area(
                "Cópia de texto do relatório:",
                relatorio_final,
                height=900,
            )

            pdf_bytes = gerar_pdf(relatorio_final)
            codigo_arquivo = st.session_state["snapshot_relatorio"]["codigo_identificacao"]
            st.download_button(
                label="📥 Baixar Relatório em PDF",
                data=pdf_bytes,
                file_name=f"CESASCORE_{codigo_arquivo}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    # =====================================================
    # RODAPÉ INSTITUCIONAL
    # =====================================================
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")

    col_margem_esq, col1, col2, col3, col_margem_dir = st.columns([4, 1, 1, 1, 4])

    with col1:
        try:
            st.image("1.jpg", use_container_width=True)
        except Exception:
            st.caption("CIPE")
    with col2:
        try:
            st.image("2.png", use_container_width=True)
        except Exception:
            st.caption("UEPA")
    with col3:
        try:
            st.image("3.png", use_container_width=True)
        except Exception:
            st.caption("CAPES")

    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])

    with col_f1:
        st.markdown("**CESASCORE**")
        st.markdown(
            "<div style='text-align:justify;font-size:14px;color:gray;'>"
            "Plataforma acadêmica de apoio à predição da via de parto, com processamento de variáveis maternas, "
            "obstétricas e fetais, incluindo cálculo automático do Índice de Bishop e Classificação de Robson."
            "</div>",
            unsafe_allow_html=True,
        )

    with col_f2:
        st.markdown("**Sobre o Projeto**")
        st.markdown(
            "<div style='text-align:justify;font-size:14px;color:gray;'>"
            "Produto técnico desenvolvido no âmbito do Programa de Pós-Graduação em Cirurgia e Pesquisa Experimental "
            "(PPG-CIPE), com foco na inovação tecnológica aplicada à saúde materna e à qualificação do cuidado obstétrico."
            "</div>",
            unsafe_allow_html=True,
        )

    with col_f3:
        st.markdown("**Contato**")
        st.markdown(
            "<div style='font-size:14px;color:gray;'>"
            "julianacostafurtado@gmail.com<br>Belém, Pará, Brasil"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;font-size:12px;color:gray;'>"
        "© 2026 Produto Técnico de Mestrado – CESASCORE.<br>Todos os direitos reservados."
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
