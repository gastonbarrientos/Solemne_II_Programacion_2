import pandas as pd

def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza general:
    - Elimina columna interna '_id' si existe
    - Intenta convertir columnas numéricas cuando sea posible
    """
    df = df.copy()

    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col], errors="ignore")

    return df
