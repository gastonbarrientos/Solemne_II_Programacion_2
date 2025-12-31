import streamlit as st
import pandas as pd

# Importación de tus módulos locales
from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

# 1. Configuración de la página
st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")
st.write("Consume datos desde **datos.gob.cl** vía **API GET**, analiza con pandas y visualiza interactivamente.")

# 2. Inicializar el estado de la sesión para persistencia de datos
if 'df' not in st.session_state:
    st.session_state.df = None

# 3. Sidebar para configuración
with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input(
        "resource_id (UUID del recurso)",
        value=DEFAULT_RESOURCE_ID,
        help="Este valor viene precargado con un recurso público de datos.gob.cl.",
    )
    limit = st.number_input("Límite de registros", min_value=10, max_value=50000, value=1000, step=10)
    load_btn = st.button("Cargar datos", use_container_width=True)

st.info("📌 El resource_id está precargado. Puedes cambiarlo por cualquier otro dataset que tenga DataStore habilitado.")

# 4. Lógica de carga de datos
if load_btn:
    if not resource_id.strip():
        st.error("Ingresa un resource_id válido.")
    else:
        try:
            with st.spinner("Descargando datos..."):
                df_raw = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
                st.session_state.df = preparar_datos(df_raw)
                st.success(f"Datos cargados: {len(st.session_state.df):,} registros")
        except Exception as e:
            st.error(f"No se pudieron cargar los datos: {e}")

# 5. Visualización y Filtros (solo si hay datos cargados)
if st.session_state.df is not None:
    df = st.session_state.df

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
            st.warning("Demasiados valores únicos para mostrar lista. Usa la búsqueda en la tabla.")

    # --- Sección de Gráficos Nativos de Streamlit ---
    st.divider()
    st.subheader("📈 Visualización de Datos")
    
    tipo_grafico = st.radio("Selecciona tipo de gráfico:", ["Barras", "Líneas", "Área"], horizontal=True)

    numeric_cols = df_view.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        col_y, col_x = st.columns(2)
        with col_y:
            num_col = st.selectbox("Eje Y (Numérico)", numeric_cols)
        with col_x:
            label_cols = df_view.select_dtypes(include=['object']).columns.tolist()
            label_col = st.selectbox("Eje X (Etiqueta)", ["(índice)"] + label_cols)

        top_n = st.slider("Mostrar Top N", 5, 50, 15)
        plot_df = df_view.sort_values(num_col, ascending=False).head(top_n)

        if label_col != "(índice)":
            plot_df = plot_df.set_index(label_col)

        if tipo_grafico == "Barras":
            st.bar_chart(plot_df[num_col])
        elif tipo_grafico == "Líneas":
            st.line_chart(plot_df[num_col])
        else:
            st.area_chart(plot_df[num_col])
    else:
        st.warning("No se detectaron columnas numéricas para graficar.")

    st.subheader("🧾 Tabla de datos")
    st.dataframe(df_view, use_container_width=True)
