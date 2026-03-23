import time
import logging
import requests
from app.config import REQUEST_TIMEOUT, MAX_RETRIES


def get_with_retry(url, params):
    """Hace un GET con reintentos ante fallos de red."""
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            # 401 significa API key inválida, no tiene sentido reintentar
            if response.status_code == 401:
                raise Exception("API Key inválida — verifica EIA_API_KEY en tu archivo .env")

            response.raise_for_status()
            return response.json()

        except Exception as e:
            if "API Key inválida" in str(e):
                raise

            last_error = e
            logging.warning(f"Intento {attempt}/{MAX_RETRIES} fallido: {e}")

            if attempt < MAX_RETRIES:
                time.sleep(2)

    logging.error(f"Todos los reintentos fallaron. Último error: {last_error}")
    raise Exception(f"No se pudo conectar después de {MAX_RETRIES} intentos: {last_error}")
