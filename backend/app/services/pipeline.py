import logging
import pandas as pd

from app.services.extractor  import fetch_outages
from app.services.validator  import validate_data
from app.services.transformer import transform_outages, create_aggregations
from app.services.storage    import get_last_period, save_raw, save_transformed


def run_pipeline():
    """Ejecuta el pipeline completo: extrae, valida, transforma y guarda."""
    logging.info("Iniciando pipeline")

    # 1. Extracción
    raw_data = fetch_outages()

    if not raw_data:
        logging.warning("La API no devolvió registros")
        return {"status": "no_data", "records": 0}

    # 2. Convertir a DataFrame y limpiar tipos
    df = pd.DataFrame(raw_data)
    df = df[["period", "capacity", "outage", "percentOutage"]]

    df["capacity"]      = pd.to_numeric(df["capacity"],      errors="coerce")
    df["outage"]        = pd.to_numeric(df["outage"],        errors="coerce")
    df["percentOutage"] = pd.to_numeric(df["percentOutage"], errors="coerce")
    df["period"]        = pd.to_datetime(df["period"])
    df = df.sort_values("period").reset_index(drop=True)

    # 3. Validación
    validate_data(df)

    # 4. Filtro incremental — solo procesar registros nuevos
    last_period = get_last_period()
    if last_period:
        df = df[df["period"] > last_period].reset_index(drop=True)
        logging.info(f"Registros nuevos después de {last_period.date()}: {len(df)}")

    if df.empty:
        logging.info("No hay datos nuevos")
        return {"status": "up_to_date", "records": 0}

    # 5. Guardar crudo
    save_raw(df)

    # 6. Transformar y guardar
    clean_df = transform_outages(df)
    stats_df = create_aggregations(clean_df)
    save_transformed(clean_df, stats_df)

    logging.info(f"Pipeline completado — {len(df)} registros nuevos procesados")

    return {
        "status":      "success",
        "records":     len(df),
        "period_from": str(df["period"].min().date()),
        "period_to":   str(df["period"].max().date()),
    }
