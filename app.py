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
st.write(
    "Aplicación desarrollada en Python y Streamlit para el análisis y "
    "visualización de datos obtenidos desde una API REST pública del Gobierno de Chile."
)

# --------------------------------------------------
# FUNCIÓN PARA CARGAR DATOS DESDE LA API
# --------------------------------------------------
@st.cache_data
def cargar_datos(resource_id, limit):
    url = "https://api.datos.gob.cl/datastreams/metadata.json"
    params = {
        "resource_id": resource_id,
        "limit": limit
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return pd.DataFrame()

    json_data = response.json()
    registros = json_data.get("result", {}).get("records", [])

    return pd.DataFrame(registros)

# --------------------------------------------------
# SIDEBAR - CONFIGURACIÓN
# --------------------------------------------------
st.sidebar.header("⚙️ Configuración")

resource_id = st.sidebar.text_input(
    "resource_id (UUID del recurso con DataStore)",
    value="2c44d782-3365-44e3-aefb-2c"
)

limit = st.sidebar.number_input(
    "Límite de registros",
    min_value=10,
    max_value=1000,
    value=50,
    step=10
)

btn_cargar = st.sidebar.button("Cargar datos")

# --------------------------------------------------
# PROCESO PRINCIPAL
# --------------------------------------------------
if btn_cargar:

    df = cargar_datos(resource_id, limit)

    if df.empty:
        st.error("❌ No se pudieron cargar datos desde la API.")
        st.stop()

    # Mostrar datos
    st.subheader("📋 Vista previa de los datos")
    st.dataframe(df)

    # --------------------------------------------------
    # SECCIÓN DE GRÁFICOS
    # --------------------------------------------------
    st.subheader("📊 Visualización de datos")

    # Columnas válidas
    columnas_numericas = df.select_dtypes(include="number").columns.tolist()
    columnas_categoricas = df.select_dtypes(exclude="number").columns.tolist()

    if not columnas_numericas:
        st.warning("No existen columnas numéricas disponibles para graficar.")
        st.stop()

    # Selector columna numérica
    col_numerica = st.selectbox(
        "Columna numérica",
        columnas_numericas
    )

    # Opción de usar columna categórica
    usar_etiqueta = st.checkbox("Usar columna categórica como etiqueta")

    col_etiqueta = None
    if usar_etiqueta:
        col_etiqueta = st.selectbox(
            "Columna categórica",
            columnas_categoricas
        )

    top_n = st.slider(
        "Top N (por valor)",
        min_value=1,
        max_value=20,
        value=10
    )

    # --------------------------------------------------
    # PROCESAMIENTO SEGURO
    # --------------------------------------------------
    if col_etiqueta:
        datos = (
            df.groupby(col_etiqueta)[col_numerica]
            .count()
            .sort_values(ascending=False)
            .head(top_n)
        )
        titulo = f"Distribución por {col_etiqueta}"
        xlabel = col_etiqueta
        ylabel = "Cantidad de registros"
    else:
        datos = (
            df[col_numerica]
            .value_counts()
            .head(top_n)
        )
        titulo = f"Distribución de {col_numerica}"
        xlabel = col_numerica
        ylabel = "Cantidad"

    # --------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------
    if datos.empty:
        st.warning("No hay datos suficientes para generar el gráfico.")
    else:
        fig, ax = plt.subplots()
        datos.plot(kind="bar", ax=ax)
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

else:
    st.info("👈 Configure los parámetros y presione **Cargar datos** para comenzar.")
