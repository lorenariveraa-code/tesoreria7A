import streamlit as st
import pandas as pd

# 1. Configuración de Pantalla
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A")
st.markdown("---")

# 2. Conexión a los datos
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(url)
    df = df.fillna("") 
    
    # Buscamos las columnas por posición (la 3era suele ser monto, la 4ta detalle, etc)
    # Pero para estar seguros, buscamos por palabras clave ignorando mayúsculas
    col_monto = [c for c in df.columns if 'monto' in c.lower()][0]
    col_tipo = [c for c in df.columns if 'tipo' in c.lower()][0]
    col_detalle = [c for c in df.columns if 'detalle' in c.lower() or 'evento' in c.lower()][0]
    
    df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0).astype(int)

    # 3. Resumen Superior (Saldo Total)
    ingresos = df[df[col_tipo].str.contains('Ingreso', case=False, na=False)][col_monto].sum()
    egresos = df[df[col_tipo].str.contains('Egreso', case=False, na=False)][col_monto].sum()
    saldo = ingresos - egresos

    st.metric("💰 Total Ingresos", f"${ingresos:,.0f}")
    st.metric("🏦 Saldo Real en Caja", f"${saldo:,.0f}")
    st.markdown("---")

    # 4. Pestañas con nombres simplificados para que NO FALLEN
    st.markdown("### 📋 Movimientos Registrados")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Cuotas", "Operativos", "Eventos", "Solidaria", "Otros"])

    def filtrar(palabra, objeto_tab):
        with objeto_tab:
            # Buscamos CUALQUIER fila que tenga esa palabra en el detalle
            mask = df[col_detalle].str.contains(palabra, case=False, na=False)
            sub_df = df[mask]
            if not sub_df.empty:
                st.dataframe(sub_df, hide_index=True)
                total = sub_df[sub_df[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum()
                st.write(f"**Total en esta sección: ${total:,.0f}**")
            else:
                st.info(f"No se encontraron datos con la palabra '{palabra}'")

    # Usamos palabras cortas que SIEMPRE están en tus categorías
    filtrar("Cuota", tab1)
    filtrar("Operativo", tab2)
    filtrar("Evento", tab3)
    filtrar("Solidaria", tab4)
    
    with tab5:
        # Todo lo que no entró arriba
        palabras = "Cuota|Operativo|Evento|Solidaria"
        mask_otros = ~df[col_detalle].str.contains(palabras, case=False, na=False)
        otros_df = df[mask_otros]
        if not otros_df.empty:
            st.dataframe(otros_df, hide_index=True)
        else:
            st.write("No hay otros movimientos.")

except Exception as e:
    st.error(f"Error al cargar: {e}")
