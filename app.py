import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="Exploración interactiva de datos",
    layout="wide"
)

st.title("🔍 Exploración interactiva de datos públicos")
st.write("Análisis y visualización de datos obtenidos desde la API REST de Chile.")

# Inicializar el estado de la sesión para el DataFrame
if 'df' not in st.session_state:
    st.session_state.df = None

# --------------------------------------------------
# FUNCIÓN PARA CARGAR DATOS
# --------------------------------------------------
@st.cache_data
def cargar_datos_api(resource_id, limit):
    # Nota: Asegúrate que la URL sea la correcta para registros (action/datastore_search)
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            registros = response.json().get("result", {}).get("records", [])
            df = pd.DataFrame(registros)
            # Intentar convertir columnas a números automáticamente
            return df.apply(pd.to_numeric, errors='ignore')
    except Exception as e:
        st.error(f"Error de conexión: {e}")
    return pd.DataFrame()

# --------------------------------------------------
# SIDEBAR - CONFIGURACIÓN
# --------------------------------------------------
st.sidebar.header("⚙️ Configuración")

resource_id = st.sidebar.text_input(
    "resource_id (UUID)",
    value="2c44d782-3365-44e3-aefb-2c" # Ejemplo
)

limit = st.sidebar.number_input("Límite de registros", 10, 5000, 100)

if st.sidebar.button("🚀 Cargar / Actualizar Datos"):
    with st.spinner('Obteniendo datos...'):
        nuevo_df = cargar_datos_api(resource_id, limit)
        if not nuevo_df.empty:
            st.session_state.df = nuevo_df
            st.success("¡Datos cargados con éxito!")
        else:
            st.error("No se encontraron datos o el ID es incorrecto.")

# --------------------------------------------------
# PROCESO DE VISUALIZACIÓN (Solo si hay datos cargados)
# --------------------------------------------------
if st.session_state.df is not None:
    df = st.session_state.df

    # Tabs para organizar la interfaz
    tab1, tab2 = st.tabs(["📋 Tabla de Datos", "📊 Gráficos Dinámicos"])

    with tab1:
        st.subheader("Vista previa")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader("Configuración del Gráfico")
        
        col1, col2, col3 = st.columns(3)

        # Identificar tipos de columnas
        cols_todas = df.columns.tolist()
        cols_num = df.select_dtypes(include=['number']).columns.tolist()
        
        with col1:
            col_x = st.selectbox("Eje X (Categoría)", cols_todas)
        with col2:
            # Si no hay numéricas, permitimos contar cualquier columna
            col_y = st.selectbox("Eje Y (Valor/Medida)", cols_num if cols_num else cols_todas)
        with col3:
            metodo = st.radio("Método", ["Contar registros", "Sumar valores (si es numérico)"])

        top_n = st.slider("Mostrar Top N resultados", 5, 50, 10)

        # Procesamiento de datos para el gráfico
        if metodo == "Contar registros":
            datos_grafico = df[col_x].value_counts().head(top_n)
            ylabel = "Cantidad"
        else:
            if col_y in cols_num:
                datos_grafico = df.groupby(col_x)[col_y].sum().sort_values(ascending=False).head(top_n)
                ylabel = f"Suma de {col_y}"
            else:
                st.warning("Selecciona una columna numérica para sumar.")
                datos_grafico = pd.Series()

        # Renderizado del gráfico
        if not datos_grafico.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            datos_grafico.plot(kind="bar", ax=ax, color="#1f77b4")
            ax.set_title(f"Top {top_n} por {col_x}")
            ax.set_ylabel(ylabel)
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.info("Ajusta los parámetros para generar el gráfico.")

else:
    st.info("👈 Presiona el botón en la barra lateral para cargar los datos.")
