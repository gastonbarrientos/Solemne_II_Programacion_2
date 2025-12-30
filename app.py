import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="DataViz persistente", layout="wide")

# 1. INICIALIZAR LA MEMORIA
# Si 'df_datos' no existe en la sesión, la creamos vacía
if 'df_datos' not in st.session_state:
    st.session_state.df_datos = None

st.title("📊 DataViz con datos.gob.cl")

# 2. BARRA LATERAL
st.sidebar.header("⚙️ Configuración")
resource_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Límite", 10, 1000, 100)

if st.sidebar.button("Cargar datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            registros = r.json().get("result", {}).get("records", [])
            # GUARDAMOS EN LA MEMORIA DE LA SESIÓN
            st.session_state.df_datos = pd.DataFrame(registros).apply(pd.to_numeric, errors='ignore')
            st.success("Datos cargados correctamente")
        else:
            st.error("Error al obtener datos")
    except Exception as e:
        st.error(f"Error: {e}")

# 3. CUERPO PRINCIPAL (FUERA DEL BOTÓN)
# Solo se ejecuta si hay datos guardados en la memoria (session_state)
if st.session_state.df_datos is not None:
    df = st.session_state.df_datos
    
    st.subheader("📈 Gráfico dinámico")
    
    # Estos selectores ahora NO borrarán los datos al usarlos
    columnas = df.columns.tolist()
    col_seleccionada = st.selectbox("Selecciona columna para el eje X", columnas)
    top_n = st.slider("Top N registros", 5, 20, 10)

    # Procesamiento y Gráfico
    datos_plot = df[col_seleccionada].value_counts().head(top_n)
    
    if not datos_plot.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        datos_plot.plot(kind="bar", ax=ax, color="skyblue")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    
    st.write("---")
    st.subheader("📋 Tabla de datos")
    st.dataframe(df)
else:
    # Este es el mensaje que ves en tu imagen 2
    st.info("👈 Configure los parámetros y presione 'Cargar datos' para comenzar.")
