import requests
import time
import logging
from app.config import REQUEST_TIMEOUT, MAX_RETRIES

def get_with_retry(url, params):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 401:
                raise Exception("API Key inválida")

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logging.warning(f"Intento {attempt+1} fallido: {e}")
            time.sleep(2)

    raise Exception("Fallaron todos los reintentos")