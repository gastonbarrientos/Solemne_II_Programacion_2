import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Nota: Asegúrate de que estos archivos existan en tu carpeta
from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

# 1. Configuración de la página
st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")
st.write("Consume datos desde **datos.gob.cl** vía **API GET (CKAN DataStore)**, analiza con pandas y visualiza de forma interactiva.")

# 2. Sidebar para configuración
with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input(
        "resource_id (UUID del recurso)",
        value=DEFAULT_RESOURCE_ID,
        help="Este valor viene precargado con un recurso público de datos.gob.cl.",
    )
    limit = st.number_input("Límite de registros", min_value=10, max_value=50000, value=1000, step=10)
    load_btn = st.button("Cargar datos", use_container_width=True)

st.info("📌 El resource_id está precargado. Puedes cambiarlo por cualquier otro dataset de la plataforma que tenga DataStore habilitado.")

# 3. Lógica principal al presionar el botón
if load_btn:
    if not resource_id.strip():
        st.error("Ingresa un resource_id válido.")
        st.stop()

    try:
        # Carga y limpieza
        df = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
        df = preparar_datos(df)
        st.success(f"Datos cargados: {len(df):,} registros | {len(df.columns)} columnas")
    except Exception as e:
        st.error(f"No se pudieron cargar los datos: {e}")
        st.stop()

    # --- SECCIÓN 1: EXPLORACIÓN Y FILTROS ---
    st.subheader("🔎 Exploración interactiva")
    col_filter = st.selectbox("Selecciona una columna para filtrar (opcional)", ["(sin filtro)"] + list(df.columns))

    df_view = df
    if col_filter != "(sin filtro)":
        unique_vals = df[col_filter].dropna().unique()
        if len(unique_vals) <= 200:
            chosen = st.multiselect(f"Filtrar {col_filter} por:", options=sorted(unique_vals.astype(str)))
            if chosen:
                df_view = df[df[col_filter].astype(str).isin(chosen)]
        else:
            st.warning("Demasiados valores únicos para mostrar en lista. Mostrando todos.")

    # --- SECCIÓN 2: GRÁFICOS INTERACTIVOS ---
    st.divider()
    st.subheader("📈 Visualización de Datos")
    
    # Elegir tipo de gráfico
    tipo_grafico = st.radio(
        "Selecciona el tipo de gráfico:",
        ["Barras", "Líneas", "Área"],
        horizontal=True
    )

    # Identificar columnas numéricas y de texto
    numeric_cols = [c for c in df_view.columns if str(df_view[c].dtype) in ("int64", "float64", "int32", "float32")]
    
    if numeric_cols:
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            num_col = st.selectbox("Eje Y (Valor numérico)", numeric_cols)
        with c2:
            label_cols = [c for c in df_view.columns if df_view[c].dtype == object]
            label_col = st.selectbox("Eje X (Categoría)", ["(índice)"] + label_cols)
        with c3:
            top_n = st.number_input("Top N", min_value=1, max_value=len(df_view), value=min(15, len(df_view)))

        # Preparar datos para graficar
        plot_df = df_view.sort_values(num_col, ascending=False).head(top_n)
        
        if label_col != "(índice)":
            plot_df = plot_df.set_index(label_col)
        
        # Mostrar el gráfico seleccionado
        if tipo_grafico == "Barras":
            st.bar_chart(plot_df[num_col])
        elif tipo_grafico == "Líneas":
            st.line_chart(plot_df[num_col])
        elif tipo_grafico == "Área":
            st.area_chart(plot_df[num_col])
    else:
        st.warning("No se detectaron columnas numéricas automáticas. Revisa el tipo de datos en 'preparar_datos'.")

    # --- SECCIÓN 3: TABLA DE DATOS ---
    st.divider()
    st.subheader("🧾 Vista previa de la tabla")
    st.dataframe(df_view, use_container_width=True)

    # Opción para descargar los datos filtrados
    csv = df_view.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados como CSV",
        data=csv,
        file_name='datos_chile.csv',
        mime='text/csv',
    )
