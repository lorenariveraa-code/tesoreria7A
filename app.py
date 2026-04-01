import streamlit as st
import pandas as pd

# 1. Configuración de Interfaz
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A - Villa Alegre")
st.markdown("---")

# 2. Conexión a los datos
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0).astype(int)
    # Limpieza de texto para que coincida con tus categorías
    df['Detalle o nombre del evento'] = df['Detalle o nombre del evento'].fillna('Otros').astype(str).str.strip()

    # 3. Resumen Ejecutivo (Lo primero que ven las "viejas")
    ingresos = int(df[df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum())
    egresos = int(df[df['Tipo de movimiento'] == 'Egreso']['Monto'].sum())
    saldo = ingresos - egresos

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Ingresos", f"${ingresos:,.0f}")
    with col2:
        st.metric("🏦 Saldo Disponible", f"${saldo:,.0f}")
    
    st.markdown("---")

    # 4. Los "Cajones" Oficiales del Formulario
    st.markdown("### 📋 Clasificación por Categoría Oficial")
    
    # Creamos las 5 pestañas exactas que me pediste
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Cuotas de Curso", 
        "🛠️ Gastos Operativos", 
        "🎉 Eventos y Campañas", 
        "🤝 Acción Solidaria", 
        "📎 Otros"
    ])

    # Función interna para filtrar y mostrar
    def filtrar_y_mostrar(categoria_nombre, objeto_tab):
        with objeto_tab:
            mask = df['Detalle o nombre del evento'].str.contains(categoria_nombre, case=False, na=False)
            sub_df = df[mask]
            if not sub_df.empty:
                st.table(sub_df[['Nombre del alumno', 'Monto', 'Tipo de movimiento']])
                total_cat = sub_df[sub_df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum() - sub_df[sub_df['Tipo de movimiento'] == 'Egreso']['Monto'].sum()
                st.write(f"**Balance neto de esta categoría: ${total_cat:,.0f}**")
            else:
                st.info(f"Sin movimientos en {categoria_nombre}")

    # Asignamos los datos a cada pestaña
    filtrar_y_mostrar("Cuotas de curso", tab1)
    filtrar_y_mostrar("Gastos operativos", tab2)
    filtrar_y_mostrar("Eventos y Campañas", tab3)
    filtrar_y_mostrar("Acción Solidaria", tab4)
    
    with tab5:
        # Todo lo que no está en las 4 anteriores
        mask_conocidos = df['Detalle o nombre del evento'].str.contains("Cuotas de curso|Gastos operativos|Eventos y Campañas|Acción Solidaria", case=False, na=False)
        otros_df = df[~mask_conocidos]
        if not otros_df.empty:
            st.table(otros_df[['Nombre del alumno', 'Monto', 'Detalle o nombre del evento']])
        else:
            st.write("No hay movimientos misceláneos.")

    # 5. Respaldo Legal (Boletas)
    st.markdown("---")
    # PEGA AQUÍ TU LINK DE DRIVE
    link_drive = "COPIA_AQUÍ_EL_LINK_DE_TU_CARPETA_DE_DRIVE" 
    st.link_button("📂 Ver Galería de Boletas (Comprobantes)", link_drive)

except Exception as e:
    st.error(f"Aviso: Cargando datos... ({e})")
