import streamlit as st
import pandas as pd

# Importación de tus módulos locales
from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

# 1. FUNCIÓN CON CACHÉ
# Esto guarda el resultado en el disco/memoria RAM. 
# Si usas el mismo ID y Límite, no vuelve a descargar nada de la API.
@st.cache_data(show_spinner="Consultando API de datos.gob.cl...")
def cargar_y_procesar(res_id, lim):
    raw_df = obtener_datos(resource_id=res_id, limit=lim)
    processed_df = preparar_datos(raw_df)
    return processed_df

st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con Caché y Persistencia")

# 2. INICIALIZAR SESSION STATE
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input("resource_id (UUID)", value=DEFAULT_RESOURCE_ID)
    limit = st.number_input("Límite de registros", min_value=10, value=1000)
    
    if st.button("Cargar / Actualizar datos", use_container_width=True):
        try:
            # Llamamos a la función con caché
            df_result = cargar_y_procesar(resource_id.strip(), int(limit))
            st.session_state.df = df_result
            st.success("¡Datos listos!")
        except Exception as e:
            st.error(f"Error: {e}")

st.info("📌 El resource_id está precargado. Gracias al Caché, si cambias de gráfico no habrá esperas.")

# 3. RENDERIZADO DE LA INTERFAZ
if st.session_state.df is not None:
    df = st.session_state.df

    # --- Filtros Dinámicos ---
    st.subheader("🔎 Filtros")
    col_to_filter = st.selectbox("Columna para filtrar:", ["(Sin filtro)"] + list(df.columns))
    
    df_view = df
    if col_to_filter != "(Sin filtro)":
        opciones = sorted(df[col_to_filter].astype(str).unique())
        seleccion = st.multiselect("Selecciona valores:", opciones)
        if seleccion:
            df_view = df[df[col_to_filter].astype(str).isin(seleccion)]

    # --- Gráficos (Ya no se borran al cambiar) ---
    st.divider()
    col_chart_1, col_chart_2 = st.columns([1, 3])
    
    with col_chart_1:
        st.subheader("📈 Ajustes")
        tipo = st.radio("Tipo de gráfico:", ["Barras", "Líneas", "Área"])
        
        num_cols = df_view.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df_view.select_dtypes(include=['object']).columns.tolist()

        if num_cols:
            eje_y = st.selectbox("Eje Y (Numérico):", num_cols)
            eje_x = st.selectbox("Eje X (Categoría):", ["(Índice)"] + cat_cols)
            top_n = st.slider("Top N:", 5, 100, 20)
        else:
            st.warning("No hay columnas numéricas.")
            eje_y = None

    with col_chart_2:
        if eje_y:
            df_plot = df_view.nlargest(top_n, eje_y)
            if eje_x != "(Índice)":
                df_plot = df_plot.set_index(eje_x)
            
            if tipo == "Barras":
                st.bar_chart(df_plot[eje_y])
            elif tipo == "Líneas":
                st.line_chart(df_plot[eje_y])
            else:
                st.area_chart(df_plot[eje_y])

    # --- Tabla ---
    st.divider()
    st.subheader("🧾 Vista de datos")
    st.dataframe(df_view, use_container_width=True)
else:
    st.warning("👈 Haz clic en el botón de la izquierda para cargar los datos.")
