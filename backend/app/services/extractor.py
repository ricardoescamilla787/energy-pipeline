import logging
from app.config import API_KEY, BASE_URL, PAGE_SIZE
from app.utils.http_client import get_with_retry

def fetch_outages():
    if not API_KEY:
        raise Exception("API Key no encontrada")

    all_data = []
    offset = 0

    while True:
        params = {
            "api_key": API_KEY,
            "data[0]": "capacity",
            "data[1]": "outage",
            "data[2]": "percentOutage",
            "length": PAGE_SIZE,
            "offset": offset
        }

        logging.info(f"Fetching offset={offset}")

        data = get_with_retry(BASE_URL, params)
        records = data.get("response", {}).get("data", [])

        if not records:
            logging.info("Fin de paginación")
            break

        all_data.extend(records)
        offset += PAGE_SIZE

    return all_data