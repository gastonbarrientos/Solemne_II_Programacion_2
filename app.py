import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# --- 1. FUNCIÓN DE LIMPIEZA (Basada en tu analysis.py) ---
def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- 2. CONFIGURACIÓN ---
st.set_page_config(page_title="DataViz Salud Chile", layout="wide")

if 'df_datos' not in st.session_state:
    st.session_state.df_datos = None

st.title("🏥 Exploración de Establecimientos de Salud")

# --- 3. CARGA DE DATOS ---
st.sidebar.header("⚙️ Configuración")
res_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Registros", 10, 1000, 500)

if st.sidebar.button("🚀 Cargar Datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": res_id, "limit": limit}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            st.session_state.df_datos = preparar_datos(pd.DataFrame(r.json()["result"]["records"]))
            st.sidebar.success("Datos listos.")
    except:
        st.sidebar.error("Error de conexión.")

# --- 4. FILTROS Y GRÁFICO (PERSISTENTES) ---
if st.session_state.df_datos is not None:
    df = st.session_state.df_datos.copy()

    # --- NUEVO: FILTRO POR REGIÓN ---
    st.subheader("📍 Filtrar por Ubicación")
    regiones = ["Todas"] + sorted(df["RegionGlosa"].unique().tolist())
    region_sel = st.selectbox("Selecciona una Región para enfocar el análisis:", regiones)
    
    if region_sel != "Todas":
        df = df[df["RegionGlosa"] == region_sel]

    st.divider()

    # --- CONFIGURACIÓN DEL GRÁFICO ---
    col1, col2 = st.columns(2)
    with col1:
        # Selector de columna (EstablecimientoGlosa, TipoPertenencia, etc.)
        col_graficar = st.selectbox("¿Qué quieres contar?", df.columns.tolist(), index=df.columns.get_loc("EstablecimientoGlosa") if "EstablecimientoGlosa" in df.columns else 0)
    with col2:
        top_n = st.slider("Mostrar los primeros N:", 5, 20, 10)

    # Lógica del Gráfico (Conteo de frecuencias)
    datos_conteo = df[col_graficar].value_counts().head(top_n)

    if not datos_conteo.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        # Gráfico horizontal para que los nombres de hospitales se lean bien
        datos_conteo.sort_values().plot(kind="barh", ax=ax, color="#2ecc71")
        ax.set_title(f"Distribución: {col_graficar} (Filtro: {region_sel})")
        ax.set_xlabel("Cantidad")
        st.pyplot(fig)
    else:
        st.warning("No hay datos para esta selección.")

    # Tabla detallada
    with st.expander
