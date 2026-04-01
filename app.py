import streamlit as st
import pandas as pd

# --- 1. CONFIGURACIÓN DE SEGURIDAD (Cámbialos a tu gusto) ---
USUARIO_CORRECTO = "apoderado7a"
CLAVE_CORRECTA = "7A2026"

# 2. Configuración de la App
st.set_page_config(page_title="Tesorería 7° A", page_icon="🔐", layout="wide")

# Función para verificar credenciales
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
                st.error("⚠️ Usuario o contraseña incorrectos")
        return False
    return True

# Si no está autenticado, detiene la ejecución aquí
if check_password():
    # --- TODO EL CÓDIGO DE TU APP COMIENZA AQUÍ ---
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
        df_pagos[col_monto] = pd.to_numeric(df_pagos[col_monto], errors='coerce').fillna(0).astype(int)

        ingresos = df_pagos[df_pagos[col_tipo].str.contains('Ingreso', case=False, na=False)][col_monto].sum()
        egresos = df_pagos[df_pagos[col_tipo].str.contains('Egreso', case=False, na=False)][col_monto].sum()
        st.metric("🏦 Saldo Disponible en Caja", f"${(ingresos - egresos):,.0f}")
        st.markdown("---")

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

        with tab_mora:
            st.error("### 🚨 ESTADO DE CUMPLIMIENTO POR ALUMNO")
            lista_total = sorted(df_nomina['Nombre'].tolist())
            st.subheader("📌 Cuota de Curso (Total: $30.000)")
            pagos_cuota = df_pagos[df_pagos[col_cat].str.contains("Cuota", case=False, na=False)]
            resumen_cuota = pagos_cuota.groupby(col_nombre)[col_monto].sum()

            for alumno in lista_total:
                pagado = resumen_cuota.get(alumno, 0)
                faltante = 30000 - pagado
                if pagado >= 30000: st.markdown(f"✅ **{alumno}** - AL DÍA")
                elif pagado > 0: st.markdown(f"⌛ **{alumno}** - PAGO PARCIAL (Faltan: **${faltante:,.0f}**)")
                else: st.markdown(f"🚨 **{alumno}** - DEBE EL TOTAL (**$30.000**)")

        st.markdown("---")
        st.link_button("📂 Ver Galería de Boletas (Drive)", "https://drive.google.com/")

    except Exception as e:
        st.error(f"Error de conexión: {e}")
