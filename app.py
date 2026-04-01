import streamlit as st
import pandas as pd

# 1. Configuración General
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A - Transparencia Total")
st.markdown("---")

# 2. Conexión a la Planilla
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0).astype(int)
    df['Detalle o nombre del evento'] = df['Detalle o nombre del evento'].fillna('Sin detalle').astype(str)

    # 3. Resumen Financiero Superior
    ingresos = int(df[df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum())
    egresos = int(df[df['Tipo de movimiento'] == 'Egreso']['Monto'].sum())
    saldo = ingresos - egresos

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Recaudado", f"${ingresos:,.0f}")
    with col2:
        st.metric("🏦 Saldo Real en Caja", f"${saldo:,.0f}", delta_color="normal")
    
    st.markdown("---")

    # 4. Lógica de "Cajones" Automáticos
    # Definimos las categorías que queremos separar
    categorias = ["Pascua", "Cuota Marzo", "Rifa", "Paseo"]
    
    st.markdown("### 📋 Desglose por Categorías")
    
    # Creamos pestañas para que no sea una lista infinita hacia abajo
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🐰 Pascua", "📅 Marzo", "🎟️ Rifa", "🚌 Paseo", "📎 Otros"])

    with tab1:
        mask = df['Detalle o nombre del evento'].str.contains("Pascua", case=False)
        sub_df = df[mask & (df['Tipo de movimiento'] == 'Ingreso')]
        if not sub_df.empty:
            st.table(sub_df[['Nombre del alumno', 'Monto']])
            st.write(f"**Total Pascua: ${sub_df['Monto'].sum():,.0f}**")
        else: st.write("Sin movimientos.")

    with tab2:
        mask = df['Detalle o nombre del evento'].str.contains("Marzo", case=False)
        sub_df = df[mask & (df['Tipo de movimiento'] == 'Ingreso')]
        if not sub_df.empty:
            st.table(sub_df[['Nombre del alumno', 'Monto']])
            st.write(f"**Total Marzo: ${sub_df['Monto'].sum():,.0f}**")
        else: st.write("Sin movimientos.")

    with tab3:
        mask = df['Detalle o nombre del evento'].str.contains("Rifa", case=False)
        sub_df = df[mask & (df['Tipo de movimiento'] == 'Ingreso')]
        if not sub_df.empty:
            st.table(sub_df[['Nombre del alumno', 'Monto']])
            st.write(f"**Total Rifa: ${sub_df['Monto'].sum():,.0f}**")
        else: st.write("Sin movimientos.")

    with tab4:
        mask = df['Detalle o nombre del evento'].str.contains("Paseo", case=False)
        sub_df = df[mask & (df['Tipo de movimiento'] == 'Ingreso')]
        if not sub_df.empty:
            st.table(sub_df[['Nombre del alumno', 'Monto']])
            st.write(f"**Total Paseo: ${sub_df['Monto'].sum():,.0f}**")
        else: st.write("Sin movimientos.")

    with tab5:
        # Todo lo que no cae en las categorías anteriores
        mask_all = df['Detalle o nombre del evento'].str.contains("Pascua|Marzo|Rifa|Paseo", case=False)
        sub_df = df[~mask_all & (df['Tipo de movimiento'] == 'Ingreso')]
        if not sub_df.empty:
            st.table(sub_df[['Nombre del alumno', 'Monto', 'Detalle o nombre del evento']])
        else: st.write("Sin otros movimientos.")

    # 5. Botón de Boletas
    st.markdown("---")
    link_drive = "COPIA_AQUÍ_EL_LINK_DE_TU_CARPETA_DE_DRIVE" 
    st.link_button("📂 Ver Galería de Boletas y Comprobantes", link_drive)

except Exception as e:
    st.error(f"Error: {e}")
