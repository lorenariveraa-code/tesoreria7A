import streamlit as st
import pandas as pd

# 1. Configuración General
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A - Villa Alegre")
st.markdown("---")

# 2. Conexión a Google Sheets (Pagos y Nómina)
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url_pagos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"
url_nomina = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Nomina"

try:
    df_pagos = pd.read_csv(url_pagos).fillna("")
    df_nomina = pd.read_csv(url_nomina).fillna("")
    
    # Detección de columnas
    col_monto = [c for c in df_pagos.columns if 'monto' in c.lower()][0]
    col_tipo = [c for c in df_pagos.columns if 'tipo' in c.lower()][0]
    col_cat = [c for c in df_pagos.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
    col_nombre = [c for c in df_pagos.columns if 'nombre' in c.lower()][0]
    
    df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)

    # 3. Resumen Financiero
    ingresos = df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False, na=False)][col_monto].sum()
    egresos = df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False, na=False)][col_monto].sum()
    st.metric("🏦 Saldo Disponible en Caja", f"${(ingresos - egresos):,.0f}")
    st.markdown("---")

    # 4. Pestañas de Navegación
    t1, t2, t3, t4, t5, tab_mora = st.tabs(["📅 Cuotas", "🛠️ Gastos", "🎉 Eventos", "🤝 Solidaria", "📎 Otros", "🚨 MOROSIDAD"])

    def mostrar_datos(palabra, obj_tab):
        with obj_tab:
            mask = df_pagos[col_cat].str.contains(palabra, case=False, na=False)
            if not df_pagos[mask].empty: st.dataframe(df_pagos[mask], hide_index=True)
            else: st.info(f"Sin registros de {palabra}")

    mostrar_datos("Cuota", t1)
    mostrar_datos("Operat", t2)
    mostrar_datos("Event", t3)
    mostrar_datos("Solidar", t4)

    # --- PESTAÑA DE COBRANZA INTELIGENTE ---
    with tab_mora:
        st.error("### 🚨 CONTROL DE CUMPLIMIENTO")
        lista_total = sorted(df_nomina['Nombre'].tolist())
        
        # SECCIÓN A: CUOTA DE CURSO ($30.000)
        st.subheader("📌 Cuota de Curso (Meta $30.000)")
        pagos_cuota = df_pagos[df_pagos[col_cat].str.contains("Cuota", case=False, na=False)]
        resumen_cuota = pagos_cuota.groupby(col_nombre)[col_monto].sum()

        for alumno in lista_total:
            pagado = resumen_cuota.get(alumno, 0)
            if pagado >= 30000: st.markdown(f"✅ **{alumno}** - Al día")
            elif pagado > 0: st.markdown(f"⚠️ **{alumno}** - Parcial (${pagado:,.0f} de $30.000)")
            else: st.markdown(f"🚨 **{alumno}** - PENDIENTE ($0)")

        st.markdown("---")

        # SECCIÓN B: EVENTOS Y CAMPAÑAS (Pascua, etc.)
        st.subheader("🎉 Cumplimiento de Campañas")
        # Buscamos si hay registros en la categoría 'Eventos'
        eventos_df = df_pagos[df_pagos[col_cat].str.contains("Event", case=False, na=False)]
        
        if not eventos_df.empty:
            # Vemos qué eventos existen (ej: 'Cuota Pascua')
            nombres_eventos = eventos_df[col_cat].unique()
            for ev in nombres_eventos:
                st.write(f"**Campaña: {ev}**")
                pagaron_ev = eventos_df[eventos_df[col_cat] == ev][col_nombre].unique()
                
                # Quienes faltan para ESTA campaña específica
                faltan_ev = [a for a in lista_total if a not in pagaron_ev]
                if faltan_ev:
                    for f in faltan_ev: st.markdown(f"📢 **{f}** - No ha pagado {ev}")
                else: st.success(f"👏 ¡Todos cumplieron con {ev}!")
        else:
            st.info("No hay campañas activas registradas.")

    st.markdown("---")
    st.link_button("📂 Ver Galería de Boletas", "TU_LINK_DE_DRIVE_AQUI")

except Exception as e:
    st.error(f"Configurando... Asegúrate de tener la pestaña 'Nomina' con los nombres. ({e})")
