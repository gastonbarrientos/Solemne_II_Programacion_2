import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="DataViz persistente", layout="wide")

# Inicializamos el contenedor de datos si no existe
if 'df_datos' not in st.session_state:
    st.session_state.df_datos = None

st.title("📊 Análisis de Datos con Memoria")

# 2. BARRA LATERAL (SIDEBAR)
st.sidebar.header("⚙️ Configuración")
resource_id = st.sidebar.text_input("ID del Recurso", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Registros", 10, 1000, 100)

# El botón SOLO carga los datos, no dibuja el gráfico
if st.sidebar.button("🚀 Cargar Datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            records = response.json().get("result", {}).get("records", [])
            # GUARDAMOS EN SESSION STATE PARA QUE NO SE BORRE AL FILTRAR
            st.session_state.df_datos = pd.DataFrame(records).apply(pd.to_numeric, errors='ignore')
            st.sidebar.success("Datos cargados en memoria.")
        else:
            st.sidebar.error("Error en la API.")
    except Exception as e:
        st.sidebar.error(f"Fallo de conexión: {e}")

# 3. LÓGICA DE VISUALIZACIÓN (FUERA DEL BOTÓN)
# Esto se ejecuta siempre, pero solo muestra cosas si ya cargamos datos antes
if st.session_state.df_datos is not None:
    df = st.session_state.df_datos
    
    st.subheader("🛠️ Filtros Dinámicos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Al cambiar esto, Streamlit recarga, pero como df está en session_state, no desaparece
        columna = st.selectbox("Columna para el gráfico", df.columns.tolist())
    
    with col2:
        top_n = st.slider("Ver Top N resultados", 5, 30, 10)

    # Procesamiento y Gráfico
    st.subheader(f"📈 Distribución de: {columna}")
    counts = df[columna].value_counts().head(top_n)
    
    if not counts.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        counts.plot(kind="bar", ax=ax, color="#007bff")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("No hay valores para mostrar en esta columna.")

    # Mostrar tabla abajo
    with st.expander("Ver tabla de datos crudos"):
        st.write(df)
else:
    st.info("👈 Presiona el botón 'Cargar Datos' para iniciar. Los filtros aparecerán aquí.")
