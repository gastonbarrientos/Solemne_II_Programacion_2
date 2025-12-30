import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="Exploración interactiva", layout="wide")

st.title("🔎 Exploración interactiva")

# ---------- CARGA DE DATOS ----------
@st.cache_data
def cargar_datos(resource_id, limit):
    url = "https://api.datos.gob.cl/datastreams/metadata.json"
    params = {
        "resource_id": resource_id,
        "limit": limit
    }
    r = requests.get(url, params=params)
    data = r.json()["result"]["records"]
    return pd.DataFrame(data)

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Configuración")

resource_id = st.sidebar.text_input(
    "resource_id (UUID del recurso con DataStore)",
    "2c44d782-3365-44e3-aefb-2c..."
)

limit = st.sidebar.number_input(
    "Límite de registros",
    min_value=10,
    max_value=1000,
    value=26
)

if st.sidebar.button("Cargar datos"):
    df = cargar_datos(resource_id, limit)

    if df.empty:
        st.warning("No hay datos disponibles")
        st.stop()

    st.subheader("📋 Datos cargados")
    st.dataframe(df)

    # ---------- SELECTOR DE COLUMNA ----------
    st.subheader("📊 Visualización dinámica")

    columna = st.selectbox(
        "Selecciona una columna para agrupar",
        df.columns
    )

    # ---------- PROCESAMIENTO ----------
    conteo = df[columna].value_counts().head(10)

    # ---------- GRÁFICO ----------
    fig, ax = plt.subplots()
    conteo.plot(kind="bar", ax=ax)
    ax.set_title(f"Distribución por {columna}")
    ax.set_xlabel(columna)
    ax.set_ylabel("Cantidad")

    st.pyplot(fig)
