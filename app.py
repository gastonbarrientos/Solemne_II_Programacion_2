import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# --- 1. FUNCIÓN DE TU ARCHIVO ANALYSIS.PY ---
def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Lógica de limpieza de tu archivo original"""
    df = df.copy()
    if "_id" in df.columns:
        df = df.drop(columns=["_id"])
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors="ignore")
    return df

# --- 2. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="DataViz Establecimientos", layout="wide")

# Inicializamos la memoria de la sesión (Para que no se borre al filtrar)
if 'df_memoria' not in st.session_state:
    st.session_state.df_memoria = None

st.title("📊 Exploración de Datos Públicos Chile")

# --- 3. SIDEBAR (Solo para cargar los datos) ---
st.sidebar.header("⚙️ Configuración")
res_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Registros", 10, 1000, 100)

if st.sidebar.button("🚀 Cargar Datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": res_id, "limit": limit}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            datos_raw = r.json()["result"]["records"]
            # PROCESAMOS CON TU FUNCIÓN Y GUARDAMOS EN MEMORIA
            df_limpio = preparar_datos(pd.DataFrame(datos_raw))
            st.session_state.df_memoria = df_limpio
            st.sidebar.success("¡Datos cargados con éxito!")
        else:
            st.sidebar.error("Error al obtener datos de la API")
    except Exception as e:
        st.sidebar.error(f"Fallo de conexión: {e}")

# --- 4. ÁREA DE VISUALIZACIÓN (FUERA DEL BLOQUE DEL BOTÓN) ---
# Al estar afuera, el gráfico no desaparece cuando cambias el filtro
if st.session_state.df_memoria is not None:
    # Usamos una copia para no alterar la memoria original
    df_filtrado = st.session_state.df_memoria.copy()

    st.divider()
    
    # --- FILTRO DE BÚSQUEDA ---
    st.subheader("🔍 Buscador de Texto")
    busqueda = st.text_input("Filtrar por nombre (ej: Hospital, CESFAM, Región)")
    
    if busqueda:
        # Busca el texto en todas las columnas
        mask = df_filtrado.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
        df_filtrado = df_filtrado[mask]
        st.info(f"Mostrando {len(df_filtrado)} resultados coincidentes.")

    # --- GRÁFICO ---
    st.subheader("📈 Gráfico Dinámico")
    col1, col2 = st.columns(2)
    
    with col1:
        # Selector de columna (EstablecimientoGlosa, RegionGlosa, etc.)
        opcion = st.selectbox("Selecciona columna para graficar", df_filtrado.columns.tolist())
    
    with col2:
        top_n = st.slider("Top N resultados", 5, 20, 10)

    # Lógica para generar el gráfico de barras
    conteo = df_filtrado[opcion].value_counts().head(top_n)

    if not conteo.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        conteo.plot(kind="bar", ax=ax, color="#1f77b4")
        ax.set_title(f"Top {top_n} por {opcion}")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("No hay datos que coincidan con la búsqueda.")

    # Mostrar la tabla detallada al final
    st.subheader("📋 Tabla de Detalles")
    st.dataframe(df_filtrado)

else:
    st.info("👈 Ingresa el resource_id y presiona 'Cargar Datos' en la barra lateral.")
