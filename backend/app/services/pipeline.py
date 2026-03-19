import logging
import pandas as pd
from app.services.extractor import fetch_outages
from app.services.validator import validate_data
from app.services.storage import save_parquet
from app.services.storage import get_last_period
from app.services.storage import save_transformed
from app.services.transformer import transform_outages, create_aggregations


def run_pipeline():
    logging.info("Iniciando pipeline")

    last_period = get_last_period()

    raw_data = fetch_outages()

    df = pd.DataFrame(raw_data)
    df = df[["period", "capacity", "outage", "percentOutage"]]

    df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce")
    df["outage"] = pd.to_numeric(df["outage"], errors="coerce")
    df["percentOutage"] = pd.to_numeric(df["percentOutage"], errors="coerce")

    df = df.sort_values("period")

    if last_period:
        df["period"] = pd.to_datetime(df["period"])
        logging.info(f"Filtrando datos mayores a {last_period}")
        df = df[df["period"] > last_period]

    if df.empty:
        logging.info("No hay datos nuevos")
        return

    validate_data(df)
    save_parquet(df)
    outages_df = transform_outages(df)
    stats_df = create_aggregations(df)
    save_transformed(outages_df, stats_df)

    logging.info("Pipeline completado")
