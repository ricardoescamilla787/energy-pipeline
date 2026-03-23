import pandas as pd


def build_outages_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabla principal de nuclear outages.
    Una fila por período (día), con las métricas de capacidad fuera de servicio.
    """
    result = df.copy()
    result["period"] = pd.to_datetime(result["period"])

    pct_col = "percent_outage" if "percent_outage" in result.columns else "percentOutage"
    result = result.rename(columns={pct_col: "percent_outage"})

    return result[["period", "capacity", "outage", "percent_outage"]].reset_index(drop=True)


def build_stats_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabla de estadísticas anuales.
    Responde: ¿cuánta capacidad nuclear estuvo fuera de servicio cada año?
    """
    result = df.copy()
    result["period"] = pd.to_datetime(result["period"])
    result["year"]   = result["period"].dt.year

    pct_col = "percent_outage" if "percent_outage" in result.columns else "percentOutage"

    stats = result.groupby("year").agg(
        avg_outage_mw      = ("outage",  "mean"),
        avg_percent_outage = (pct_col,   "mean"),
        max_outage_mw      = ("outage",  "max"),
        min_outage_mw      = ("outage",  "min"),
        total_records      = ("outage",  "count"),
    ).reset_index()

    return stats.round(2)
