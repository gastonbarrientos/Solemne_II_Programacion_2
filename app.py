import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1. Configuración de página
st.set_page_config(page_title="DataViz con datos.gob.cl", layout="wide")

# 2. Inicializar el estado de la sesión (Para que los datos no se borren)
if 'df' not in st.session_state:
    st.session_state.df = None

st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")

# --------------------------------------------------
# SIDEBAR - CONFIGURACIÓN
# --------------------------------------------------
st.sidebar.header("⚙️ Configuración")
resource_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Límite de registros", 10, 1000, 100)

# Al presionar el botón, guardamos los datos en session_state
if st.sidebar.button("Cargar datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            registros = response.json().get("result", {}).get("records", [])
            df_nuevo = pd.DataFrame(registros)
            # Intentar convertir columnas numéricas
            st.session_state.df = df_nuevo.apply(pd.to_numeric, errors='ignore')
            st.sidebar.success("¡Datos cargados!")
        else:
            st.sidebar.error("Error al conectar con la API")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# --------------------------------------------------
# CUERPO PRINCIPAL (Fuera del bloque del botón)
# --------------------------------------------------

# Solo mostramos esto si el dataframe ya existe en la sesión
if st.session_state.df is not None:
    df = st.session_state.df

    # --- SECCIÓN DE FILTROS Y GRÁFICO ---
    st.subheader("📈 Gráfico (elige columna)")
    
    columnas = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        # Este selector ahora no borrará nada porque df está en session_state
        col_seleccionada = st.selectbox("Selecciona columna para graficar", columnas)
    
    with col2:
        top_n = st.slider("Top N (por valor)", 1, 20, 10)

    # Procesar datos
    datos_grafico = df[col_seleccionada].value_counts().head(top_n)

    if not datos_grafico.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        datos_grafico.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title(f"Distribución de {col_seleccionada}")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    
    st.divider()
    st.subheader("📋 Tabla de datos completa")
    st.dataframe(df)

else:
    st.info("👈 Configura el resource_id y presiona 'Cargar datos' en el panel lateral.")
