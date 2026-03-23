import logging
import pandas as pd

REQUIRED_FIELDS = ["period", "capacity", "outage", "percentOutage"]


def validate_data(df: pd.DataFrame):
    """Verifica que el DataFrame tenga los campos requeridos y no esté vacío."""
    logging.info("Validando datos...")

    if df.empty:
        raise ValueError("El dataset está vacío")

    missing = [f for f in REQUIRED_FIELDS if f not in df.columns]
    if missing:
        raise ValueError(f"Campos faltantes: {missing}")

    logging.info(f"Validación OK — {len(df)} registros")
