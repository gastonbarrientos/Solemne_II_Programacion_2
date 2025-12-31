import streamlit as st
import pandas as pd

# Importación de tus módulos locales
from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz - Conexión Directa")

# 1. INICIALIZAR SESSION STATE (Fundamental para que no se borre el gráfico)
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input("resource_id (UUID)", value=DEFAULT_RESOURCE_ID)
    limit = st.number_input("Límite de registros", min_value=10, value=1000)
    
    # Al quitar el caché, la descarga ocurre CADA VEZ que presionas este botón
    if st.button("Cargar datos ahora", use_container_width=True):
        try:
            with st.spinner("Descargando datos en tiempo real..."):
                raw_data = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
                st.session_state.df = preparar_datos(raw_data)
                st.success("¡Datos actualizados!")
        except Exception as e:
            st.error(f"Error: {e}")

st.info("📌 Los datos se descargarán directamente desde la API cada vez que presiones el botón.")

# 2. RENDERIZADO (Solo si hay datos en la sesión)
if st.session_state.df is not None:
    df = st.session_state.df

    # --- Filtros ---
    st.subheader("🔎 Filtros")
    col_to_filter = st.selectbox("Columna para filtrar:", ["(Sin filtro)"] + list(df.columns))
    
    df_view = df
    if col_to_filter != "(Sin filtro)":
        opciones = sorted(df[col_to_filter].astype(str).unique())
        seleccion = st.multiselect("Selecciona valores:", opciones)
        if seleccion:
            df_view = df[df[col_to_filter].astype(str).isin(seleccion)]

    # --- Gráficos (Persistentes gracias al Session State) ---
    st.divider()
    st.subheader("📈 Visualización")
    
    # Cambiar esto NO activará una nueva descarga de datos
    tipo = st.radio("Tipo de gráfico:", ["Barras", "Líneas", "Área"], horizontal=True)

    num_cols = df_view.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df_view.select_dtypes(include=['object']).columns.tolist()

    if num_cols:
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            eje_y = st.selectbox("Eje Y (Numérico):", num_cols)
        with c2:
            eje_x = st.selectbox("Eje X (Categoría):", ["(Índice)"] + cat_cols)
        with c3:
            top_n = st.slider("Top N:", 5, 100, 20)
        
        # Preparar dataframe para el gráfico
        df_plot = df_view.nlargest(top_n, eje_y)
        if eje_x != "(Índice)":
            df_plot = df_plot.set_index(eje_x)

        if tipo == "Barras":
            st.bar_chart(df_plot[eje_y])
        elif tipo == "Líneas":
            st.line_chart(df_plot[eje_y])
        else:
            st.area_chart(df_plot[eje_y])
    else:
        st.warning("No se encontraron columnas numéricas para graficar.")

    # --- Tabla ---
    st.divider()
    st.subheader("🧾 Vista de datos")
    st.dataframe(df_view, use_container_width=True)
else:
    st.warning("👈 Haz clic en 'Cargar datos ahora' para empezar.")
