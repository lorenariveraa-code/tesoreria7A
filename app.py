import streamlit as st
import pandas as pd

# 1. Configuración de Interfaz
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A - Transparencia Total")
st.markdown("---")

# 2. Conexión a los datos
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(url)
    df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0).astype(int)
    
    # Limpieza de textos (Detalle Grande y Glosa Específica)
    df['Categoría'] = df['Detalle o nombre del evento'].fillna('Otros').astype(str).str.strip()
    # Asumimos que la columna de la 'Glosa' o detalle específico es la que sigue en tu formulario
    # Si en tu Excel la columna se llama distinto, el sistema la mostrará igual.
    df = df.fillna("")

    # 3. Resumen Ejecutivo Superior
    ingresos = int(df[df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum())
    egresos = int(df[df['Tipo de movimiento'] == 'Egreso']['Monto'].sum())
    saldo = ingresos - egresos

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Ingresos", f"${ingresos:,.0f}")
    with col2:
        st.metric("🏦 Saldo en Caja", f"${saldo:,.0f}")
    
    st.markdown("---")

    # 4. Los Cajones (Pestañas) con Detalle Específico
    st.markdown("### 📋 Movimientos por Categoría")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Cuotas de Curso", 
        "🛠️ Gastos Operativos", 
        "🎉 Eventos y Campañas", 
        "🤝 Acción Solidaria", 
        "📎 Otros"
    ])

    # Función para filtrar y mostrar con la columna de Detalle
    def mostrar_detalle_cajon(termino_busqueda, objeto_tab):
        with objeto_tab:
            mask = df['Categoría'].str.contains(termino_busqueda, case=False, na=False)
            sub_df = df[mask]
            if not sub_df.empty:
                # Aquí mostramos: Nombre, el Detalle específico (Glosa) y el Monto
                # He incluido 'Comentarios' o la columna de detalle que tengas en el form
                columnas_a_mostrar = ['Nombre del alumno', 'Monto', 'Tipo de movimiento']
                # Si existe una columna de "especifique" o "comentarios", la agregamos
                for col in df.columns:
                    if "especifique" in col.lower() or "detalle" in col.lower() and col != 'Categoría':
                        if col not in columnas_a_mostrar: columnas_a_mostrar.insert(2, col)

                st.table(sub_df[columnas_a_mostrar])
                bal = sub_df[sub_df['Tipo de movimiento'] == 'Ingreso']['Monto'].sum() - sub_df[sub_df['Tipo de movimiento'] == 'Egreso']['Monto'].sum()
                st.write(f"**Balance Neto {termino_busqueda}: ${bal:,.0f}**")
            else:
                st.info(f"No hay registros para: {termino_busqueda}")

    # Ejecutamos para cada pestaña
    mostrar_detalle_cajon("Cuotas", tab1)
    mostrar_detalle_cajon("Operativos", tab2)
    mostrar_detalle_cajon("Eventos", tab3)
    mostrar_detalle_cajon("Solidaria", tab4)
    
    with tab5:
        palabras_clave = "Cuotas|Operativos|Eventos|Solidaria"
        mask_otros = ~df['Categoría'].str.contains(palabras_clave, case=False, na=False)
        otros_df = df[mask_otros]
        if not otros_df.empty:
            st.table(otros_df)
        else:
            st.write("Sin movimientos misceláneos.")

    # 5. Link a las boletas
    st.markdown("---")
    st.link_button("📂 Ver Galería de Boletas (Comprobantes)", "TU_LINK_DE_DRIVE_AQUI")

except Exception as e:
    st.error(f"Aviso: Esperando datos... ({e})")
