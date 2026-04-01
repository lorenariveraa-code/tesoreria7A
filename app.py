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
    # Leer datos y limpiar
    df = pd.read_csv(url)
    df = df.fillna("") # Rellenar vacíos para que no den error
    
    # Intentar detectar columnas de Monto y Tipo automáticamente
    # Buscamos columnas que contengan 'Monto' o 'Tipo' sin importar mayúsculas
    col_monto = [c for c in df.columns if 'monto' in c.lower()][0]
    col_tipo = [c for c in df.columns if 'tipo' in c.lower()][0]
    col_categoria = [c for c in df.columns if 'detalle' in c.lower() or 'evento' in c.lower()][0]
    
    df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0).astype(int)

    # 3. Resumen Financiero Superior
    ingresos = int(df[df[col_tipo].str.contains('Ingreso', case=False)] [col_monto].sum())
    egresos = int(df[df[col_tipo].str.contains('Egreso', case=False)] [col_monto].sum())
    saldo = ingresos - egresos

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Total Ingresos", f"${ingresos:,.0f}")
    with col2:
        st.metric("🏦 Saldo en Caja", f"${saldo:,.0f}")
    
    st.markdown("---")

    # 4. Pestañas con Categorías Exactas del Formulario
    st.markdown("### 📋 Movimientos por Categoría Oficial")
    
    # Creamos las pestañas con tus nombres exactos
    categorias_reales = ["Cuotas de curso", "Gastos operativos", "Eventos y Campañas", "Acción Solidaria", "Otros"]
    tabs = st.tabs([f"📂 {cat}" for cat in categorias_reales])

    for i, cat_nombre in enumerate(categorias_reales):
        with tabs[i]:
            # Filtro flexible: busca la categoría exacta
            mask = df[col_categoria].str.contains(cat_nombre, case=False, na=False)
            sub_df = df[mask]
            
            if not sub_df.empty:
                # Mostramos todas las columnas para que no se pierda nada
                st.dataframe(sub_df, hide_index=True)
                
                # Cálculo de subtotal
                ing_cat = sub_df[sub_df[col_tipo].str.contains('Ingreso', case=False)][col_monto].sum()
                egr_cat = sub_df[sub_df[col_tipo].str.contains('Egreso', case=False)][col_monto].sum()
                st.write(f"**Balance {cat_nombre}: ${ing_cat - egr_cat:,.0f}**")
            else:
                st.info(f"Sin movimientos registrados en {cat_nombre}")

    # 5. Link a las boletas
    st.markdown("---")
    st.link_button("📂 Ver Galería de Boletas (Comprobantes)", "TU_LINK_DE_DRIVE_AQUI")

except Exception as e:
    st.error(f"Aviso técnico: Revisando estructura de datos... ({e})")
    # Si falla la detección automática, mostramos la tabla cruda para ver qué pasa
    st.write("Datos recibidos de Google:")
    st.dataframe(df)
