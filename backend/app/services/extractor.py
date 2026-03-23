import logging
from app.config import API_KEY, BASE_URL, PAGE_SIZE
from app.utils.http_client import get_with_retry

def fetch_outages():
    """Extrae todos los registros de la API con paginación automática."""
    if not API_KEY:
        raise Exception("EIA_API_KEY no encontrada — configúrala en el archivo .env")

    all_data = []
    offset = 0

    while True:
        params = {
            "api_key":  API_KEY,
            "data[0]":  "capacity",
            "data[1]":  "outage",
            "data[2]":  "percentOutage",
            "length":   PAGE_SIZE,
            "offset":   offset,
        }

        logging.info(f"Descargando registros desde offset={offset}")

        data    = get_with_retry(BASE_URL, params)
        records = data.get("response", {}).get("data", [])

        if not records:
            logging.info(f"Paginación completa — {len(all_data)} registros extraídos")
            break

        all_data.extend(records)
        offset += PAGE_SIZE

    return all_data
