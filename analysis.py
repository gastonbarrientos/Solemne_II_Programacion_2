import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# --- 1. FUNCIÓN DE LIMPIEZA (DE TU ARCHIVO ANALYSIS.PY) ---
def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Limpieza general basada en analysis.py"""
    df = df.copy()
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- 2. CONFIGURACIÓN Y MEMORIA ---
st.set_page_config(page_title="DataViz Establecimientos", layout="wide")

# Inicializar el estado si no existe (Crucial para que no se borre)
if 'df_final' not in st.session_state:
    st.session_state.df_final = None

st.title("📊 DataViz con datos.gob.cl")

# --- 3. SIDEBAR PARA CARGAR ---
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
            # Aplicamos tu limpieza de analysis.py y guardamos en memoria
            st.session_state.df_final = preparar_datos(pd.DataFrame(raw_records))
            st.sidebar.success("¡Datos cargados y limpios!")
        else:
            st.sidebar.error("Error en la API")
    except:
        st.sidebar.error("Error de conexión")

# --- 4. VISUALIZACIÓN (FUERA DEL BOTÓN) ---
# Al estar fuera del botón, los filtros ya no borrarán el gráfico
if st.session_state.df_final is not None:
    df = st.session_state.df_final

    st.subheader("🔍 Exploración Interactiva")
    
    # Buscador de texto
    busqueda = st.text_input("Buscar establecimiento o región...")
    if busqueda:
        mask = df.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        df_display = df[mask]
    else:
        df_display = df

    # Selectores de gráfico
    col1, col2 = st.columns(2)
    with col1:
        # Los nombres de columnas como 'EstablecimientoGlosa' aparecerán aquí
        col_x = st.selectbox("Selecciona columna para graficar", df_display.columns.tolist())
    with col2:
        top_n = st.slider("Top N", 5, 20, 10)

    # Gráfico de barras
    conteo = df_display[col_x].value_counts().head(top_n)
    if not conteo.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        conteo.plot(kind="bar", ax=ax, color="skyblue")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    
    st.dataframe(df_display)
else:
    st.info("👈 Presiona 'Cargar Datos' para comenzar.")
