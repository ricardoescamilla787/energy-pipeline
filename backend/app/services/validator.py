import logging
import pandas as pd

REQUIRED_FIELDS = ["period", "capacity", "outage", "percentOutage"]

def validate_data(df: pd.DataFrame):
    logging.info("Validando datos...")

    if df.empty:
        raise Exception("Dataset vacío")

    for field in REQUIRED_FIELDS:
        if field not in df.columns:
            raise Exception(f"Campo faltante: {field}")

    if df[REQUIRED_FIELDS].isnull().any().any():
        raise Exception("Valores nulos en campos críticos")

    logging.info("Validación OK")