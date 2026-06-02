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

    # --- Alerta Interativo de Parto Cesáreo Anterior ---
    tempo_cesarea = None
    if partos_cesareos > 0:
        st.warning("⚠️ Paciente com histórico de Parto Cesáreo Anterior")
        tempo_cesarea = st.radio(
            "Há quanto tempo ocorreu o último parto cesáreo?",
            ["Menos de 2 anos (< 24 meses)", "Mais de 2 anos (≥ 24 meses)"]
        )

    st.markdown("") # Um pequeno espaço para "respirar" na tela
    
    # --- Datação da Gestação (DUM) ---
    st.subheader("Datação da Gestação")
    col_dum, col_ig_dum, col_dpp_dum = st.columns(3)
    
    with col_dum:
        dum = st.date_input("DUM (Última Menstruação)", value=None, format="DD/MM/YYYY")
    
    with col_ig_dum:
        # A IG só aparece se a DUM for preenchida
        if dum:
            dias_gest = (hoje - dum).days # Usa a variável 'hoje' criada no Bloco 1
            if dias_gest >= 0:
                ig_sem = dias_gest // 7
                ig_dias = dias_gest % 7
                st.metric("IG (pela DUM)", f"{ig_sem} sem e {ig_dias} dias")
            else:
                st.metric("IG (pela DUM)", "Data no futuro")
        else:
            st.metric("IG (pela DUM)", "---")
            
    with col_dpp_dum:
        # A DPP (280 dias após a DUM) só aparece se a DUM for preenchida
        if dum:
            dpp_calc = dum + timedelta(days=280)
            st.metric("DPP (pela DUM)", dpp_calc.strftime('%d/%m/%Y'))
        else:
            st.metric("DPP (pela DUM)", "---")

    # --- Datação da Gestação (USG) ---
    col_eco, col_ig_eco, col_dpp_eco = st.columns(3)
    
    with col_eco:
        dpp_eco = st.date_input("DPP pela 1ª USG (Eco)", value=None, format="DD/MM/YYYY")
    
    with col_ig_eco:
        if dpp_eco:
            # Se temos a DPP da USG, calculamos de trás pra frente (DPP - 280 = dia da concepção)
            dt_concepcao_eco = dpp_eco - timedelta(days=280)
            dias_gest_eco = (hoje - dt_concepcao_eco).days
            if dias_gest_eco >= 0:
                ig_sem_eco = dias_gest_eco // 7
                ig_dias_eco = dias_gest_eco % 7
                st.metric("IG (pela USG)", f"{ig_sem_eco} sem e {ig_dias_eco} dias")
            else:
                st.metric("IG (pela USG)", "Data muito distante")
        else:
            st.metric("IG (pela USG)", "---")
            
    with col_dpp_eco:
        # Apenas refletimos visualmente a DPP escolhida para manter a simetria
        if dpp_eco:
            st.metric("DPP (pela USG)", dpp_eco.strftime('%d/%m/%Y'))
        else:
            st.metric("DPP (pela USG)", "---")

    st.markdown("---")
    # --- FIM DO BLOCO 2 ---
