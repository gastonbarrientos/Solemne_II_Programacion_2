import streamlit as st
import matplotlib.pyplot as plt

from data_api import obtener_datos
from analysis import preparar_datos

DEFAULT_RESOURCE_ID = "2c44d782-3365-44e3-aefb-2c8b8363a1bc"

st.set_page_config(page_title="DataViz - datos.gob.cl", layout="wide")
st.title("📊 DataViz con datos.gob.cl (API REST + Streamlit)")
st.write("Consume datos desde **datos.gob.cl** vía **API GET (CKAN DataStore)**, analiza con pandas y visualiza con matplotlib.")

with st.sidebar:
    st.header("🔧 Configuración")
    resource_id = st.text_input(
        "resource_id (UUID del recurso con DataStore)",
        value=DEFAULT_RESOURCE_ID,
        help="Este valor viene precargado con un recurso público de datos.gob.cl. Puedes reemplazarlo por otro resource_id.",
    )
    limit = st.number_input("Límite de registros", min_value=10, max_value=50000, value=1000, step=10)
    load_btn = st.button("Cargar datos")

st.info("📌 El resource_id está precargado con un recurso de **datos.gob.cl**. Puedes cambiarlo si usas otro dataset con DataStore habilitado.")

if load_btn:
    if not resource_id.strip():
        st.error("Ingresa un resource_id válido.")
        st.stop()

    try:
        df = obtener_datos(resource_id=resource_id.strip(), limit=int(limit))
        df = preparar_datos(df)
    except Exception as e:
        st.error(f"No se pudieron cargar los datos: {e}")
        st.stop()

    st.success(f"Datos cargados: {len(df):,} registros | {len(df.columns)} columnas")

    st.subheader("🔎 Exploración interactiva")
    col_filter = st.selectbox("Selecciona una columna para filtrar (opcional)", ["(sin filtro)"] + list(df.columns))

    df_view = df
    if col_filter != "(sin filtro)":
        unique_vals = df[col_filter].dropna().unique()
        if len(unique_vals) <= 200:
            chosen = st.multiselect(f"Filtrar {col_filter} por:", options=sorted(unique_vals.astype(str)))
            if chosen:
                df_view = df[df[col_filter].astype(str).isin(chosen)]
        else:
            st.warning("Demasiados valores únicos para filtro por lista. Usa búsqueda en la tabla.")

    st.subheader("📈 Gráfico (elige columna numérica)")
    numeric_cols = [c for c in df_view.columns if str(df_view[c].dtype) in ("int64", "float64", "int32", "float32")]
    if numeric_cols:
        num_col = st.selectbox("Columna numérica", numeric_cols)
        top_n = st.slider("Top N (por valor)", 5, 50, 10)

        label_cols = [c for c in df_view.columns if df_view[c].dtype == object]
        label_col = st.selectbox("Columna etiqueta (opcional)", ["(índice)"] + label_cols)

        plot_df = df_view.sort_values(num_col, ascending=False).head(top_n)

        fig, ax = plt.subplots()
        y_labels = plot_df.index.astype(str) if label_col == "(índice)" else plot_df[label_col].astype(str)
        ax.barh(y_labels, plot_df[num_col])
        ax.invert_yaxis()
        ax.set_xlabel(num_col)
        ax.set_ylabel(label_col if label_col != "(índice)" else "Índice")
        st.pyplot(fig)
    else:
        st.warning("No se detectaron columnas numéricas en el dataset cargado para graficar.")

    st.subheader("🧾 Tabla de datos")
    st.dataframe(df_view, use_container_width=True)


cambiale el tipo de grafico
