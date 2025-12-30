import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1. PEGA AQUÍ LA FUNCIÓN DE TU ARCHIVO ANALYSIS.PY
def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# 2. CONFIGURACIÓN DE STREAMLIT
st.set_page_config(page_title="DataViz", layout="wide")

# Inicializar memoria (Esto evita que se borre al filtrar)
if 'df_final' not in st.session_state:
    st.session_state.df_final = None

st.title("📊 DataViz con datos.gob.cl")

# 3. SIDEBAR (Configuración y Carga)
st.sidebar.header("Configuración")
resource_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Registros", 10, 1000, 100)

if st.sidebar.button("🚀 Cargar Datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            raw_records = r.json()["result"]["records"]
            # Guardamos los datos limpios en la memoria global
            st.session_state.df_final = preparar_datos(pd.DataFrame(raw_records))
            st.sidebar.success("¡Datos cargados!")
    except:
        st.sidebar.error("Error de conexión")

# 4. VISUALIZACIÓN (DEBE IR FUERA DEL IF DEL BOTÓN)
if st.session_state.df_final is not None:
    df = st.session_state.df_final
    
    # Aquí es donde el usuario elige la columna (como EstablecimientoGlosa)
    # Al estar fuera del botón, Streamlit no lo borra al cambiar la opción
    col_x = st.selectbox("Selecciona columna para graficar", df.columns.tolist())
    
    # Lógica del gráfico
    conteo = df[col_x].value_counts().head(10)
    fig, ax = plt.subplots()
    conteo.plot(kind="bar", ax=ax)
    st.pyplot(fig)
    
    st.dataframe(df)
else:
    st.info("👈 Presiona 'Cargar Datos' para comenzar.")
