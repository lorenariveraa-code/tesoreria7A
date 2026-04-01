import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. SEGURIDAD ---
USUARIO_CORRECTO = "apoderado7a"
CLAVE_CORRECTA = "7A2026"

st.set_page_config(page_title="Tesorería 7° A", page_icon="🔐", layout="wide")

def check_password():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if not st.session_state["autenticado"]:
        st.title("🔐 Acceso Privado - Tesorería 7° A")
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == USUARIO_CORRECTO and password == CLAVE_CORRECTA:
                st.session_state["autenticado"] = True
                st.rerun()
            else: st.error("⚠️ Credenciales incorrectas")
        return False
    return True

if check_password():
    st.title("📊 Control de Caja 7° A - Villa Alegre")
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"autenticado": False}))
    
    sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
    url_pagos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"
    url_nomina = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Nomina"

    try:
        df_pagos = pd.read_csv(url_pagos).fillna("")
        df_nomina = pd.read_csv(url_nomina).fillna("")
        
        col_monto = [c for c in df_pagos.columns if 'monto' in c.lower()][0]
        col_tipo = [c for c in df_pagos.columns if 'tipo' in c.lower()][0]
        col_cat = [c for c in df_pagos.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
        col_nombre = [c for c in df_pagos.columns if 'nombre' in c.lower()][0]
        col_glosa = [c for c in df_pagos.columns if 'especifique' in c.lower() or ('detalle' in c.lower() and c != col_cat)][0]

        df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)
        df_pagos[col_nombre] = df_pagos[col_nombre].str.strip()
        df_nomina['Nombre'] = df_nomina['Nombre'].str.strip()
        df_pagos[col_glosa] = df_pagos[col_glosa].str.strip().str.capitalize()

        st.metric("🏦 Saldo en Caja", f"${(df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum() - df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()):,.0f}")
        st.markdown("---")

        t1, t2, t3, t4, t5, tab_mora = st.tabs(["📅 Cuotas", "🛠️ Gastos", "🎉 Eventos", "🤝 Solidaria", "📎 Otros", "🚨 ESTADO DE PAGOS"])

        def mostrar_datos(palabra, obj_tab):
            with obj_tab:
                mask = df_pagos[col_cat].str.contains(palabra, case=False, na=False)
                if not df_pagos[mask].empty: st.dataframe(df_pagos[mask], hide_index=True)
                else: st.info(f"Sin registros")

        mostrar_datos("Cuota", t1); mostrar_datos("Operat", t2); mostrar_datos("Event", t3); mostrar_datos("Solidar", t4)

        with tab_mora:
            st.error("### 🚨 CONTROL DE PAGOS PENDIENTES")
            
            # --- EXPLICACIÓN DEL SISTEMA ---
            with st.expander("ℹ️ ¿Cómo funciona este sistema de cobro? (Haz clic para leer)"):
                st.write("""
                Para facilitar el pago, la cuota anual de **$30.000** se ha dividido en **10 cuotas mensuales de $3.000** (de marzo a diciembre).
                
                * Cada cuota vence el **día 5 de cada mes**.
                * El sistema calcula automáticamente cuántas cuotas han vencido a la fecha de hoy.
                * Si has pagado más del total vencido, aparecerás **Al Día**.
                * Si has pagado el total de los $30.000, aparecerás con una **Estrella** de agradecimiento.
                """)

            # --- CÁLCULO DE CUOTAS VENCIDAS ---
            hoy = datetime.now()
            mes_actual = hoy.month
            dia_actual = hoy.day
            
            if mes_actual < 3: meses_vencidos = 0
            elif mes_actual > 12: meses_vencidos = 10
            else:
                meses_vencidos = mes_actual - 3 
                if dia_actual >= 5: meses_vencidos += 1 
            
            cuota_mensual = 3000
            deuda_exigible = meses_vencidos * cuota_mensual
            
            st.info(f"📅 **Corte al día de hoy:** {meses_vencidos} meses devengados (Monto exigible: ${deuda_exigible:,.0f})")
            
            lista_total = sorted(df_nomina['Nombre'].tolist())
            pagos_cuota = df_pagos[df_pagos[col_cat].str.contains("Cuota", case=False, na=False)]
            resumen_cuota = pagos_cuota.groupby(col_nombre)[col_monto].sum()

            for a in lista_total:
                p = resumen_cuota.get(a, 0)
                if p >= 30000:
                    st.markdown(f"🌟 **{a}** - PAGADO EL AÑO COMPLETO")
                elif p >= deuda_exigible and deuda_exigible > 0:
                    st.markdown(f"✅ **{a}** - AL DÍA (Pagado: ${p:,.0f})")
                elif p > 0:
                    st.markdown(f"⌛ **{a}** - PENDIENTE (Debe: ${deuda_exigible - p:,.0f} de lo vencido)")
                elif deuda_exigible > 0:
                    st.markdown(f"🚨 **{a}** - PENDIENTE (Debe: ${deuda_exigible:,.0f} a la fecha)")
                else:
                    st.markdown(f"✅ **{a}** - Sin deudas vencidas")

            st.markdown("---")
            # SECCIÓN CAMP
