import streamlit as st
import pandas as pd

# Importación de tus módulos locales
from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

# 1. Configuración de la página
st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")

# 2. Inicialización de sesión (Evita que los datos se borren al cambiar de gráfico)
if 'df' not in st.session_state:
    st.session_state.df = None

# 3. Sidebar (Barra Lateral)
with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input(
        "resource_id (UUID del recurso)",
        value=DEFAULT_RESOURCE_ID,
        help="El ID se encuentra en la URL del recurso en datos.gob.cl",
    )
    limit = st.number_input("Límite de registros", min_value=10, value=1000)
    
    # Botón de carga: Guarda los datos en session_state
    if st.button("Cargar datos", use_container_width=True):
        try:
            with st.spinner("Descargando..."):
                df_raw = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
                st.session_state.df = preparar_datos(df_raw)
                st.success("¡Datos cargados!")
        except Exception as e:
            st.error(f"Error: {e}")

# 4. Mensaje informativo (st.info)
st.info("📌 El resource_id está precargado. Puedes cambiarlo por cualquier otro dataset de la plataforma que tenga DataStore habilitado.")

# 5. Visualización de contenido
if st.session_state.df is not None:
    df = st.session_state.df

    # --- Filtros ---
    st.subheader("🔎 Filtros")
    col_filter = st.selectbox("Filtrar por columna:", ["(Sin filtro)"] + list(df.columns))
    
    df_view = df
    if col_filter != "(Sin filtro)":
        unique_vals = df[col_filter].dropna().unique()
        chosen = st.multiselect(f"Selecciona valores de {col_filter}:", options=sorted(unique_vals.astype(str)))
        if chosen:
            df_view = df[df[col_filter].astype(str).isin(chosen)]

    # --- Gráficos Interactivos ---
    st.divider()
    st.subheader("📈 Visualización")
    
    # El uso de session_state permite que cambiar este radio NO borre los datos
    tipo = st.radio("Selecciona tipo de gráfico:", ["Barras", "Líneas", "Área"], horizontal=True)

    numeric_cols = df_view.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        col_y = st.selectbox("Columna numérica (Eje Y):", numeric_cols)
        top_n = st.slider("Mostrar Top N registros:", 5, 50, 15)
        
        # Preparar datos para el gráfico
        plot_df = df_view.nlargest(top_n, col_y)

        # Renderizado de gráficos nativos de Streamlit
        if tipo == "Barras":
            st.bar_chart(plot_df[col_y])
        elif tipo == "Líneas":
            st.line_chart(plot_df[col_y])
        else:
            st.area_chart(plot_df[col_y])
    else:
        st.warning("No hay columnas numéricas para graficar.")

    # --- Tabla Final ---
    st.subheader("🧾 Vista de datos")
    st.dataframe(df_view, use_container_width=True)
else:
    st.warning("👈 Haz clic en 'Cargar datos' en el panel izquierdo para comenzar.")
