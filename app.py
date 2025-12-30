import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(
    page_title="DataViz – Exploración Interactiva",
    layout="wide"
)

st.title("🔍 Exploración interactiva de datos públicos")
st.write("Aplicación desarrollada con Python y Streamlit utilizando datos abiertos del Gobierno de Chile.")

# ---------------- FUNCIÓN CARGA DE DATOS ----------------
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

    data = response.json()
    records = data.get("result", {}).get("records", [])
    return pd.DataFrame(records)

# ---------------- SIDEBAR ----------------
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

cargar = st.sidebar.button("Cargar datos")

# ---------------- PROCESAMIENTO ----------------
if cargar:
    df = cargar_datos(resource_id, limit)

    if df.empty:
        st.error("❌ No se pudieron cargar los datos desde la API.")
        st.stop()

    st.subheader("📋 Vista previa de los datos")
    st.dataframe(df)

    # ---------------- SELECCIÓN DE COLUMNAS ----------------
    st.subheader("📊 Visualización dinámica")

    columnas_numericas = df.select_dtypes(include="number").columns.tolist()
    columnas_categoricas = df.select_dtypes(exclude="number").columns.tolist()

    if not columnas_numericas:
        st.warning("No existen columnas numéricas para graficar.")
        st.stop()

    col_numerica = st.selectbox(
        "Columna numérica",
        columnas_numericas
    )

    col_etiqueta = st.selectbox(
        "Columna etiqueta (opcional)",
        ["(ninguna)"] + columnas_categoricas
    )

    top_n = st.slider(
        "Top N (por valor)",
        min_value=1,
        max_value=20,
        value=10
    )

    # ---------------- LÓGICA DE GRAFICACIÓN SEGURA ----------------
    if col_etiqueta != "(ninguna)":
        datos = (
            df.groupby(col_etiqueta)[col_numerica]
            .count()
            .sort_values(ascending=False)
            .head(top_n)
        )
        xlabel = col_etiqueta
        ylabel = "Cantidad de registros"
        titulo = f"Distribución por {col_etiqueta}"
    else:
        datos = (
            df[col_numerica]
            .value_counts()
            .head(top_n)
        )
        xlabel = col_numerica
        ylabel = "Cantidad"
        titulo = f"Distribución de {col_numerica}"

    # ---------------- VALIDACIÓN FINAL ----------------
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
    st.info("👈 Configura los parámetros y presiona **Cargar datos** para comenzar.")
