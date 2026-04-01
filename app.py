import streamlit as st
import pandas as pd

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
        
        # Identificar columnas
        col_monto = [c for c in df_pagos.columns if 'monto' in c.lower()][0]
        col_tipo = [c for c in df_pagos.columns if 'tipo' in c.lower()][0]
        col_cat = [c for c in df_pagos.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
        col_nombre = [c for c in df_pagos.columns if 'nombre' in c.lower()][0]
        
        # BUSCAMOS LA COLUMNA DE GLOSA (donde dice 'Pascua')
        # Buscamos una columna que diga "especifique", "glosa" o que NO sea la de categoría principal
        col_glosa = [c for c in df_pagos.columns if 'especifique' in c.lower() or 'detalle' in c.lower() and c != col_cat]
        col_glosa = col_glosa[0] if col_glosa else col_cat # Si no hay, usa la categoría

        df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)

        st.metric("🏦 Saldo en Caja", f"${(df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum() - df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()):,.0f}")
        st.markdown("---")

        t1, t2, t3, t4, t5, tab_mora = st.tabs(["📅 Cuotas", "🛠️ Gastos", "🎉 Eventos", "🤝 Solidaria", "📎 Otros", "🚨 MOROSIDAD"])

        def mostrar_datos(palabra, obj_tab):
            with obj_tab:
                mask = df_pagos[col_cat].str.contains(palabra, case=False, na=False)
                if not df_pagos[mask].empty: st.dataframe(df_pagos[mask], hide_index=True)
                else: st.info(f"Sin registros")

        mostrar_datos("Cuota", t1); mostrar_datos("Operat", t2); mostrar_datos("Event", t3); mostrar_datos("Solidar", t4)

        with tab_mora:
            st.error("### 🚨 ESTADO DE CUMPLIMIENTO")
            lista_total = sorted(df_nomina['Nombre'].tolist())
            
            # SECCIÓN A: CUOTA DE CURSO
            st.subheader("📌 Cuota de Curso ($30.000)")
            pagos_cuota = df_pagos[df_pagos[col_cat].str.contains("Cuota", case=False, na=False)]
            resumen_cuota = pagos_cuota.groupby(col_nombre)[col_monto].sum()
            for a in lista_total:
                p = resumen_cuota.get(a, 0)
                if p >= 30000: st.markdown(f"✅ **{a}** - AL DÍA")
                elif p > 0: st.markdown(f"⌛ **{a}** - PAGO PARCIAL (Faltan: ${30000-p:,.0f})")
                else: st.markdown(f"🚨 **{a}** - DEBE EL TOTAL ($30.000)")

            st.markdown("---")

            # SECCIÓN B: CAMPAÑAS ESPECÍFICAS (CON GLOSA)
            st.subheader("🎉 Cumplimiento de Campañas")
            ev_df = df_pagos[df_pagos[col_cat].str.contains("Event", case=False, na=False)]
            
            if not ev_df.empty:
                # Creamos una columna combinada: "Eventos (Pascua)"
                ev_df['Evento_Detallado'] = ev_df[col_cat] + " (" + ev_df[col_glosa].astype(str) + ")"
                tipos_eventos = ev_df['Evento_Detallado'].unique()
                
                for ev_nom in tipos_eventos:
                    st.markdown(f"🔍 **Revisando: {ev_nom}**")
                    pagaron = ev_df[ev_df['Evento_Detallado'] == ev_nom][col_nombre].unique()
                    faltan = [al for al in lista_total if al not in pagaron]
                    if faltan:
                        for deudor in faltan:
                            st.markdown(f"🚨 **{deudor}** - PENDIENTE (**{ev_nom}**)")
                    else: st.success(f"👏 Todo el curso cumplió con {ev_nom}!")
            else: st.info("No hay campañas aún.")

        st.link_button("📂 Ver Galería de Boletas", "https://drive.google.com/")

    except Exception as e: st.error(f"Error: {e}")
