import streamlit as st
import pandas as pd

# 1. Título
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊")
st.title("📊 Control de Caja 7° A")
st.markdown("---")

# 2. Conexión
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0).astype(int)

    # 3. Resumen Simple
    ingresos = int(df[df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum())
    saldo = ingresos - int(df[df['Tipo de movimiento'] == 'Egreso']['Monto'].sum())

    st.subheader(f"💰 Total Recaudado: ${ingresos:,.0f}")
    st.subheader(f"🏦 Saldo en Caja: ${saldo:,.0f}")
    st.markdown("---")

    # 4. Detalle de Pascua (Versión Manual Sin Errores)
    st.markdown("### 🐰 Pagos Recibidos: Cuota de Pascua")
    
    pascua_df = df[df['Detalle o nombre del evento'].astype(str).str.contains("Pascua", case=False, na=False)]
    
    if not pascua_df.empty:
        # Aquí escribimos la lista línea por línea para evitar a Numpy
        for index, row in pascua_df.iterrows():
            st.markdown(f"* **{row['Nombre del alumno']}**: ${int(row['Monto']):,.0f}")
        
        total_pascua = int(pascua_df['Monto'].sum())
        st.markdown(f"**Total Pascua: ${total_pascua:,.0f}**")
    else:
        st.write("No hay registros de Pascua aún.")

except Exception as e:
    st.error(f"Error: {e}")