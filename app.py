import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# 1. Configuración inicial
st.set_page_config(page_title="Explorador de Datos", layout="wide")

# 2. Inicializar el estado de la sesión (ESTO ES CLAVE)
# Si no hacemos esto, el DataFrame se borra al mover un slider o selectbox
if 'df_final' not in st.session_state:
    st.session_state.df_final = None

st.title("🔍 Exploración de Datos Públicos")

# 3. Sidebar
st.sidebar.header("⚙️ Configuración")
resource_id = st.sidebar.text_input("resource_id", value="2c44d782-3365-44e3-aefb-2c44d782-3365-44e3-aefb-2c")
limit = st.sidebar.number_input("Límite", 10, 1000, 50)

# 4. Función de carga
@st.cache_data
def obtener_datos(res_id, lim):
    # URL correcta para obtener registros en la API de datos.gob.cl
    url = f"https://api.datos.gob.cl/api/action/datastore_search"
    params = {"resource_id": res_id, "limit": lim}
    try:
        r = requests.get(url, params=params)
        if r.status_code == 200:
            data = r.json()
            records = data.get("result", {}).get("records", [])
            df = pd.DataFrame(records)
            # Convertir columnas a números si es posible
            return df.apply(pd.to_numeric, errors='ignore')
    except Exception as e:
        st.error(f"Error: {e}")
    return pd.DataFrame()

# 5. Lógica del Botón
if st.sidebar.button("Cargar datos"):
    # Guardamos el resultado en el session_state
    resultado = obtener_datos(resource_id, limit)
    if not resultado.empty:
        st.session_state.df_final = resultado
        st.success("Datos cargados!")
    else:
        st.error("No se encontraron datos.")

# 6. Renderizado (Fuera del bloque del botón)
# Esto permite que el gráfico no desaparezca al interactuar
if st.session_state.df_final is not None:
    df = st.session_state.df_final
    
    st.subheader("📋 Vista previa")
    st.dataframe(df.head())

    st.subheader("📊 Gráfico")
    
    # Filtramos columnas para los selectores
    columnas = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    with col1:
        eje_x = st.selectbox("Selecciona columna para el eje X", columnas)
    with col2:
        top_n = st.slider("Cantidad de registros", 5, 20, 10)

    # Procesar datos para el gráfico
    # Contamos las ocurrencias de la columna seleccionada
    datos_plot = df[eje_x].value_counts().head(top_n)

    if not datos_plot.empty:
        fig, ax = plt.subplots()
        datos_plot.plot(kind="bar", ax=ax)
        ax.set_title(f"Top {top_n} de {eje_x}")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("No hay datos para mostrar.")
else:
    st.info("👈 Haz clic en 'Cargar datos' en el panel de la izquierda.")
