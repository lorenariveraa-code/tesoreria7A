import streamlit as st
import pandas as pd

# 1. Configuración de la Aplicación (Diseño ancho para celular)
st.set_page_config(page_title="Tesorería 7° A", page_icon="📊", layout="wide")
st.title("📊 Control de Caja 7° A - Villa Alegre")
st.markdown("---")

# 2. Conexión a tu Planilla de Google
sheet_id = "1GjmhdSc-Aw8HUdVW2Xuy5DOtcBxUnos1C02_ARFGWVM"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    # Leer y limpiar datos
    df = pd.read_csv(url)
    df = df.fillna("") # Evita errores si hay celdas vacías
    
    # Identificar columnas automáticamente por palabras clave
    col_monto = [c for c in df.columns if 'monto' in c.lower()][0]
    col_tipo = [c for c in df.columns if 'tipo' in c.lower()][0]
    col_detalle = [c for c in df.columns if 'detalle' in c.lower() or 'evento' in c.lower() or 'categor' in c.lower()][0]
    
    # Convertir montos a números enteros
    df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0).astype(int)

    # 3. Resumen Financiero Principal (Saldo)
    ingresos = df[df[col_tipo].str.contains('Ingreso', case=False, na=False)][col_monto].sum()
    egresos = df[df[col_tipo].str.contains('Egreso', case=False, na=False)][col_monto].sum()
    saldo = ingresos - egresos

    # Mostrar métricas grandes arriba
    c1, c2 = st.columns(2)
    with c1:
        st.metric("💰 Total Ingresos", f"${ingresos:,.0f}")
    with c2:
        st.metric("🏦 Saldo Actual (Caja)", f"${saldo:,.0f}")
    
    st.markdown("---")

    # 4. Los "Cajones" (Pestañas) con búsqueda flexible
    st.markdown("### 📋 Movimientos por Categoría")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Cuotas", 
        "🛠️ Gastos Op.", 
        "🎉 Eventos", 
        "🤝 Solidaria", 
        "📎 Otros"
    ])

    # Función para filtrar datos sin importar mayúsculas o plurales
    def filtrar_y_mostrar(palabra_clave, objeto_tab):
        with objeto_tab:
            # Buscamos la raíz de la palabra para no fallar
            mask = df[col_detalle].str.contains(palabra_clave, case=False, na=False)
            sub_df = df[mask]
            if not sub_df.empty:
                # Mostramos la tabla con los datos
                st.dataframe(sub_df, hide_index=True)
                # Sumamos ingresos y restamos egresos de esa pestaña
                total_cat = sub_df[sub_df[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum() - \
                            sub_df[sub_df[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()
                st.write(f"**Balance Neto de esta sección: ${total_cat:,.0f}**")
            else:
                st.info(f"No hay registros que contengan '{palabra_clave}'")

    # Asignamos las palabras clave cortas para asegurar que el sistema las encuentre
    filtrar_y_mostrar("Cuota", tab1)      # Busca "Cuotas de curso"
    filtrar_y_mostrar("Operat", tab2)    # Busca "Gastos operativos"
    filtrar_y_mostrar("Event", tab3)     # Busca "Eventos y campañas" (Aquí aparecerá Pascua)
    filtrar_y_mostrar("Solidar", tab4)   # Busca "Acción Solidaria"
    
    with tab5:
        # Aquí cae todo lo que no coincida con las palabras anteriores
        claves = "Cuota|Operat|Event|Solidar"
        mask_otros = ~df[col_detalle].str.contains(claves, case=False, na=False)
        otros_df = df[mask_otros]
        if not otros_df.empty:
            st.dataframe(otros_df, hide_index=True)
        else:
            st.write("No hay movimientos adicionales.")

    # 5. Sección de Boletas
    st.markdown("---")
    st.subheader("🕵️‍♀️ Respaldo de Comprobantes")
    # Pon aquí el link de tu carpeta de Google Drive si lo tienes
    st.link_button("📂 Ver Fotos de Boletas y Recibos", "https://drive.google.com/")

except Exception as e:
    st.error(f"Aviso: El sistema se está actualizando o hay un detalle en la planilla. ({e})")
