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
    st.title("📊 Control de Caja 7° A")
    st.sidebar.button("Cerrar Sesión", on_click=lambda: st.session_state.update({"autenticado": False}))
    
    sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
    url_pagos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"
    url_nomina = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Nomina"
    url_avisos = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Avisos"

    try:
        df_pagos = pd.read_csv(url_pagos).fillna("")
        df_nomina = pd.read_csv(url_nomina).fillna("")
        df_avisos = pd.read_csv(url_avisos).fillna("")
        
        # Identificación dinámica de columnas
        col_monto = [c for c in df_pagos.columns if 'monto' in c.lower()][0]
        col_tipo = [c for c in df_pagos.columns if 'tipo' in c.lower()][0]
        col_cat = [c for c in df_pagos.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
        col_nombre = [c for c in df_pagos.columns if 'nombre' in c.lower()][0]
        col_glosa = [c for c in df_pagos.columns if 'especifique' in c.lower() or ('detalle' in c.lower() and c != col_cat)][0]
        col_link = [c for c in df_pagos.columns if 'comprobante' in c.lower() or 'archivo' in c.lower() or 'foto' in c.lower()][0]

        df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)
        df_pagos[col_nombre] = df_pagos[col_nombre].str.strip()
        df_nomina['Nombre'] = df_nomina['Nombre'].str.strip()
        df_pagos[col_glosa] = df_pagos[col_glosa].str.strip().str.upper()

        # --- CABECERA ---
        ingresos = df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum()
        egresos = df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()
        st.metric("🏦 Saldo Actual en Caja", f"${(ingresos - egresos):,.0f}")

        if not df_avisos.empty:
            mensaje_actual = df_avisos.iloc[0, 0]
            st.info(f"📢 **INFORMACIÓN IMPORTANTE:** \n\n {mensaje_actual}")

        st.markdown("---")
        t1, t2, t3, t4, t5, tab_mora = st.tabs(["📅 Cuotas", "🛠️ GASTOS (TODOS)", "🎉 Eventos", "🤝 Solidaria", "📎 Otros", "🚨 PAGOS"])

        # --- PESTAÑA GASTOS CON LINKS FUNCIONALES ---
        with t2:
            mask_egresos = df_pagos[col_tipo].str.contains('Egreso', case=False)
            if not df_pagos[mask_egresos].empty:
                st.subheader("📋 Detalle de Dinero Saliente")
                st.dataframe(
                    df_pagos[mask_egresos], 
                    hide_index=True,
                    column_config={col_link: st.column_config.LinkColumn("Ver Comprobante 📄")}
                )
                st.warning(f"**Total Egresado hasta hoy:** ${egresos:,.0f}")
            else:
                st.info("No hay egresos registrados.")

        def mostrar_ingresos(palabra, obj_tab):
            with obj_tab:
                mask = (df_pagos[col_cat].str.contains(palabra, case=False, na=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))
                if not df_pagos[mask].empty: st.dataframe(df_pagos[mask], hide_index=True)
                else: st.info(f"Sin ingresos registrados")

        mostrar_ingresos("Cuota", t1); mostrar_ingresos("Event", t3); mostrar_ingresos("Solidar", t4); mostrar_ingresos("Otros", t5)

        # --- PESTAÑA DE CONTROL DE PAGOS ---
        with tab_mora:
            st.error("### 🚨 CONTROL DE PAGOS")
            with st.expander("ℹ️ ¿Cómo funciona este sistema de cuotas?"):
                st.write("Cuota anual de $30.000 (10 cuotas de $3.000, vencen el día 5 de cada mes).")

            hoy = datetime.now()
            mes_actual = hoy.month
            dia_actual = hoy.day
            if mes_actual < 3: meses_vencidos = 0
            elif mes_actual > 12: meses_vencidos = 10
            else:
                meses_vencidos = mes_actual - 3 
                if dia_actual >= 5: meses_vencidos += 1 
            
            deuda_exigible = meses_vencidos * 3000
            st.info(f"📅 **Monto exigible a la fecha:** ${deuda_exigible:,.0f} ({meses_vencidos} cuotas)")
            
            lista_total = sorted(df_nomina['Nombre'].tolist())
            resumen_cuota = df_pagos[(df_pagos[col_cat].str.contains("Cuota", case=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))].groupby(col_nombre)[col_monto].sum()

            for a in lista_total:
                p = resumen_cuota.get(a, 0)
                if p >= 30000: st.markdown(f"🌟 **{a}** - PAGADO COMPLETO")
                elif p >= deuda_exigible and deuda_exigible > 0: st.markdown(f"✅ **{a}** - AL DÍA")
                elif p > 0: st.markdown(f"⌛ **{a}** - PENDIENTE (Faltan: ${deuda_exigible - p:,.0f})")
                elif deuda_exigible > 0: st.markdown(f"🚨 **{a}** - PENDIENTE (Debe: ${deuda_exigible:,.0f})")
                else: st.markdown(f"✅ **{a}** - AL DÍA")

            st.markdown("---")
            st.subheader("🎉 Campañas 🐰🥕")
            ev_df = df_pagos[(df_pagos[col_cat].str.contains("Event", case=False, na=False)) & (df_pagos[col_tipo].str.contains('Ingreso', case=False))]
            if not ev_df.empty:
                campanas_unicas = sorted([g for g in ev_df[col_glosa].unique() if g != ""])
                for ev_nom in campanas_unicas:
                    st.write(f"🔍 **Campaña: {ev_nom}**")
                    pagaron = ev_df[ev_df[col_glosa] == ev_nom][col_nombre].unique()
                    faltan = [al for al in lista_total if al not in pagaron]
                    if faltan:
                        for deudor in faltan: st.markdown(f"🚨 **{deudor}** - PENDIENTE")
                    else: st.success(f"👏 ¡Todos cumplieron!")

        # --- BOTÓN DE GALERÍA INTELIGENTE ---
        # Intenta extraer la carpeta base de los links existentes en el Excel
        links_existentes = df_pagos[df_pagos[col_link].str.contains("drive.google.com", na=False)][col_link]
        if not links_existentes.empty:
            # Si hay links, el botón usará la carpeta de tus comprobantes
            ejemplo_link = links_existentes.iloc[0]
            link
