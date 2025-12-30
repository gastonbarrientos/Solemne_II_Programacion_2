import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1. Configuración de página
st.set_page_config(page_title="DataViz Establecimientos", layout="wide")

# 2. INICIALIZAR LA MEMORIA (Esto evita que se borre al filtrar)
if 'df_datos' not in st.session_state:
    st.session_state.df_datos = None

st.title("📊 Visualización de Datos de Salud")

# 3. BARRA LATERAL PARA CARGA
st.sidebar.header("⚙️ Configuración")
resource_id = st.sidebar.text_input("ID del Recurso", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Registros", 10, 1000, 100)

if st.sidebar.button("🚀 Cargar Datos"):
    url = "https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": resource_id, "limit": limit}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            registros = r.json().get("result", {}).get("records", [])
            # Guardamos el DataFrame en session_state
            df = pd.DataFrame(registros)
            st.session_state.df_datos = df.apply(pd.to_numeric, errors='ignore')
            st.sidebar.success("¡Datos cargados con éxito!")
        else:
            st.sidebar.error("No se pudo conectar con la API")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# 4. CUERPO PRINCIPAL (FUERA DEL BOTÓN)
# Solo se muestra si ya cargamos datos antes
if st.session_state.df_datos is not None:
    df = st.session_state.df_datos
    
    st.subheader("🔍 Filtros y Gráfico")
    
    col1, col2 = st.columns(2)
    with col1:
        # Ahora al cambiar esto, el script se reinicia pero los datos siguen en st.session_state
        col_seleccionada = st.selectbox("Selecciona columna para el eje X", df.columns.tolist())
    with col2:
        top_n = st.slider("Ver Top N resultados", 5, 20, 10)

    # Procesamiento de datos para el gráfico
    conteo = df[col_seleccionada].value_counts().head(top_n)

    if not conteo.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        conteo.plot(kind="bar", ax=ax, color="#4CB391")
        ax.set_title(f"Distribución por {col_seleccionada}")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    
    st.write("---")
    st.subheader("📋 Tabla de datos")
    st.dataframe(df)
else:
    st.info("👈 Ingresa los datos y presiona 'Cargar Datos' en la izquierda para empezar.")
