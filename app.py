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
            else: 
                st.error("⚠️ Credenciales incorrectas")
        return False
    return True

if check_password():
    st.title("📊 Control de Caja 7° A")
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"autenticado": False}))
    
    sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
    url_pagos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"
    url_nomina = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Nomina"
    url_avisos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Avisos"

    try:
        # Carga de datos
        df_pagos = pd.read_csv(url_pagos).fillna("")
        df_nomina = pd.read_csv(url_nomina).fillna("")
        df_avisos = pd.read_csv(url_avisos).fillna("")
        
        # Identificación de columnas
        col_monto = [c for c in df_pagos.columns if 'monto' in c.lower()][0]
        col_tipo = [c for c in df_pagos.columns if 'tipo' in c.lower()][0]
        col_cat = [c for c in df_pagos.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
        col_nombre = [c for c in df_pagos.columns if 'nombre' in c.lower()][0]
        col_glosa = [c for c in df_pagos.columns if 'especifique' in c.lower() or ('detalle' in c.lower() and c != col_cat)][0]
        col_link = [c for c in df_pagos.columns if 'comprobante' in c.lower() or 'archivo' in c.lower() or 'foto' in c.lower()][0]

        # Limpieza
        df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)
        df_pagos[col_nombre] = df_pagos[col_nombre].str.strip()
        df_nomina['Nombre'] = df_nomina['Nombre'].str.strip()
        df_pagos[col_glosa] = df_pagos[col_glosa].str.strip().str.upper()

        # Cabecera - Saldo
        ingresos_tot = df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum()
        egresos_tot = df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()
        st.metric("🏦 Saldo Actual en Caja", f"${(ingresos_tot - egresos_tot):,.0f}")

        # Cabecera - Avisos
        if not df_avisos.empty:
            mensaje = df_avisos.iloc[0, 0]
            st.info(f"📢 **INFORMACIÓN IMPORTANTE:** \n\n {mensaje}")

        st.markdown("---")
        t1, t2, t3, t4, t5, tab_mora = st.tabs(["📅 Cuotas", "🛠️ GASTOS", "🎉 Eventos", "🤝 Solidaria", "📎 Otros", "🚨 PAGOS"])

        # Pestaña Gastos (Links activos)
        with t2:
            mask_eg = df_pagos[col_tipo].str.contains('Egreso', case=False)
            if not df_pagos[mask_eg].empty:
                st.subheader("📋 Detalle de Gastos")
                st.dataframe(
                    df_pagos[mask_eg], 
                    hide_index=True,
                    column_config={col_link: st.column_config.LinkColumn("Archivo 📄")}
                )
                st.warning(f"**Total Gastado:** ${egresos_tot:,.0f}")
            else:
                st.info("Sin gastos registrados.")

        def mostrar_ing(palabra, obj_tab):
            with obj_tab:
                m = (df_pagos[col_cat].str.contains(palabra, case=False, na=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))
                if not df_pagos[m].empty: st.dataframe(df_pagos[m], hide_index=True)
                else: st.info(f"Sin ingresos de {palabra}")

        mostrar_ing("Cuota", t1); mostrar_ing("Event", t3); mostrar_ing("Solidar", t4); mostrar_ing("Otros", t5)

        with tab_mora:
            st.error("### 🚨 CONTROL DE PAGOS")
            with st.expander("ℹ️ ¿Cómo funciona el sistema?"):
                st.write("Cuota anual $30.000 (10 x $3.000). Vencen el día 5 de cada mes.")

            h = datetime.now()
            mv = (h.month - 3) + (1 if h.day >= 5 else 0) if 3 <= h.month <= 12 else (10 if h.month > 12 else 0)
            exigible = mv * 3000
            st.info(f"📅 **Monto exigible hoy:** ${exigible:,.0f} ({mv} cuotas)")
            
            lista = sorted(df_nomina['Nombre'].tolist())
            pagos = df_pagos[(df_pagos[col_cat].str.contains("Cuota", case=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))].groupby(col_nombre)[col_monto].sum()

            for a in lista:
                p = pagos.get(a, 0)
                if p >= 30000: st.markdown(f"🌟 **{a}** - PAGADO COMPLETO")
                elif p >= exigible and exigible > 0: st.markdown(f"✅ **{a}** - AL DÍA")
                elif p > 0: st.markdown(f"⌛ **{a}** - PENDIENTE (Falta: ${exigible - p:,.0f})")
                elif exigible > 0: st.markdown(f"🚨 **{a}** - PENDIENTE (Debe: ${exigible:,.0f})")
                else: st.markdown(f"✅ **{a}** - AL DÍA")

            st.markdown("---")
            st.subheader("🎉 Campañas 🐰🥕")
            ev = df_pagos[(df_pagos[col_cat].str.contains("Event", case=False, na=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))]
            if not ev.empty:
                for ev_nom in sorted([g for g in ev[col_glosa].unique() if g != ""]):
                    st.write(f"🔍 **Campaña: {ev_nom}**")
                    pagaron = ev[ev[col_glosa] == ev_nom][col_nombre].unique()
                    faltan = [al for al in lista if al not in pagaron]
                    if faltan:
                        for deudor in faltan: st.markdown(f"🚨 **{deudor}** - PENDIENTE")
                    else: st.success(f"👏 ¡Todo el curso pagó {ev_nom}!")

        st.link_button("📂 Ver Galería de Boletas", "https://drive.google.com/")

    except Exception as e:
        st.error(f"Error técnico: {e}")
