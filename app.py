# ==========================================
    # BLOCO 1: IDENTIFICAÇÃO
    # ==========================================
    st.header("1. Identificação")
    
    # --- Primeira Linha: Dados Pessoais ---
    c1, c2, c3 = st.columns([2, 1, 1])
    
    with c1:
        nome = st.text_input("Nome da Paciente", placeholder="Digite o nome completo")
        
    with c2:
        # st.date_input recebe a data. O format="DD/MM/YYYY" garante o padrão brasileiro.
        data_nasc = st.date_input("Data de Nascimento", value=None, format="DD/MM/YYYY")
        
    with c3:
        # Lógica para calcular a idade automaticamente
        idade = None
        if data_nasc:
            hoje = date.today()
            # Cálculo exato considerando se a paciente já fez aniversário no ano atual
            idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
            st.metric("Idade Calculada", f"{idade} anos")
        else:
            st.metric("Idade Calculada", "---")

    # --- Segunda Linha: Antropometria ---
    c4, c5, c6 = st.columns(3)
    
    with c4:
        # format="%.1f" permite casas decimais (ex: 70.5)
        peso_kg = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="Ex: 70.5")
        
    with c5:
        # format="%.2f" permite duas casas decimais, ideal para metros (ex: 1.60)
        altura_m = st.number_input("Altura (metros)", min_value=1.00, max_value=2.50, value=None, step=0.01, format="%.2f", placeholder="Ex: 1.60")
        
    with c6:
        # Lógica para calcular o IMC automaticamente
        imc = None
        if peso_kg is not None and altura_m is not None and altura_m > 0:
            imc = peso_kg / (altura_m ** 2)
            st.metric("IMC Automático", f"{imc:.1f} kg/m²")
        else:
            st.metric("IMC Automático", "---")

    st.markdown("---")
    # --- FIM DO BLOCO 1 ---
