import requests
import pandas as pd

CKAN_BASE = "https://datos.gob.cl"
DATASTORE_SEARCH = f"{CKAN_BASE}/api/3/action/datastore_search"


def obtener_datos(resource_id: str, limit: int = 1000) -> pd.DataFrame:
    """
    Obtiene datos desde el DataStore de datos.gob.cl usando API REST (GET).

    Args:
        resource_id: UUID del recurso (resource_id) en datos.gob.cl con DataStore habilitado.
        limit: Cantidad máxima de registros a traer.

    Returns:
        DataFrame con los registros.

    Raises:
        ValueError: Si la API no responde correctamente o el recurso no existe/no tiene DataStore.
        requests.RequestException: Si falla la conexión.
    """
    params = {"resource_id": resource_id, "limit": int(limit)}

    try:
        resp = requests.get(DATASTORE_SEARCH, params=params, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Error de conexión a datos.gob.cl: {e}") from e

    if not isinstance(payload, dict) or "success" not in payload:
        raise ValueError("Respuesta inesperada de la API CKAN (formato inválido).")

    if payload.get("success") is not True:
        error_msg = payload.get("error", {}).get("message", "Error desconocido desde la API.")
        raise ValueError(f"La API respondió success=False: {error_msg}")

    result = payload.get("result", {})
    records = result.get("records", [])

    if not records:
        raise ValueError(
            "No se obtuvieron registros. Verifica que el resource_id exista y tenga DataStore habilitado."
        )

    return pd.DataFrame(records)

