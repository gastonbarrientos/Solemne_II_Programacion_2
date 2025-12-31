st.subheader("📈 Visualización de Datos")
    
    # 1. Selección de tipo de gráfico
    tipo_grafico = st.radio(
        "Selecciona el tipo de gráfico:",
        ["Barras", "Líneas", "Área"],
        horizontal=True
    )

    numeric_cols = [c for c in df_view.columns if str(df_view[c].dtype) in ("int64", "float64", "int32", "float32")]
    
    if numeric_cols:
        col1, col2 = st.columns(2)
        with col1:
            num_col = st.selectbox("Eje Y (Numérico)", numeric_cols)
        with col2:
            label_cols = [c for c in df_view.columns if df_view[c].dtype == object]
            label_col = st.selectbox("Eje X (Etiqueta)", ["(índice)"] + label_cols)

        top_n = st.slider("Mostrar Top N registros", 5, 50, 15)

        # Preparar datos para el gráfico
        plot_df = df_view.sort_values(num_col, ascending=False).head(top_n)
        
        # Definir el índice para el eje X
        if label_col != "(índice)":
            plot_df = plot_df.set_index(label_col)
        
        # Renderizar según la selección
        if tipo_grafico == "Barras":
            st.bar_chart(plot_df[num_col])
        elif tipo_grafico == "Líneas":
            st.line_chart(plot_df[num_col])
        elif tipo_grafico == "Área":
            st.area_chart(plot_df[num_col])
            
    else:
        st.warning("No se detectaron columnas numéricas para graficar.")
