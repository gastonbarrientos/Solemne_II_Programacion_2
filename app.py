import streamlit as st
import pandas as pd

# Importación de tus módulos locales
from data_api import obtener_datos
from analysis import preparar_datos

# Configuración inicial
DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")

# Inicializar st.session_state para que los datos no se borren al cambiar gráficos
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar para configuración
with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input(
        "resource_id (UUID del recurso)",
        value=DEFAULT_RESOURCE_ID,
        help="El ID se encuentra en la URL del recurso en datos.gob.cl",
    )
    limit = st.number_input("Límite de registros", min_value=10, value=1000)
    load_btn = st.button("Cargar datos", use_container_width=True)

# Mensaje informativo
st.info("📌 El resource_id está precargado. Puedes cambiarlo por cualquier otro dataset de la plataforma que tenga DataStore habilitado.")

# Procesamiento de carga
if load_btn:
    try:
        with st.spinner("Descargando datos..."):
            df_raw = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
            st.session_state.df = preparar_datos(df_raw)
            st.success("¡Datos cargados correctamente!")
    except Exception as e:
        st.error(f"Error al cargar: {e}")

# Visualización (Solo si hay datos cargados)
if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("🔎 Filtros y Exploración")
    col_to_filter = st.selectbox("Filtrar por columna:", ["(Sin filtro)"] + list(df.columns))
    
    df_view = df
    if col_to_filter != "(Sin filtro)":
        opciones = sorted(df[col_to_filter].astype(str).unique())
        seleccion = st.multiselect(f"Valores de {col_to_filter}:", opciones)
        if seleccion:
            df_view = df[df[col_to_filter].astype(str).isin(seleccion)]

    st.divider()
    
    # Sección de Gráficos Nativos de Streamlit (No se borran al cambiar el tipo)
    st.subheader("📈 Visualización Interactiva")
    tipo = st.radio("Tipo de gráfico:", ["Barras", "Líneas", "Área"], horizontal=True)

    num_cols = df_view.select_dtypes(include=['number']).columns.tolist()
    if num_cols:
        col_y = st.selectbox("Eje Y (Numérico):", num_cols)
        top_n = st.slider("Ver Top N:", 5, 50, 15)
        
        plot_df = df_view.nlargest(top_n, col_y)

        if tipo == "Barras":
            st.bar_chart(plot_df[col_y])
        elif tipo == "Líneas":
            st.line_chart(plot_df[col_y])
        else:
            st.area_chart(plot_df[col_y])
    else:
        st.warning("No se detectaron columnas numéricas para graficar.")

    st.subheader("🧾 Tabla de Datos")
    st.dataframe(df_view, use_container_width=True)
