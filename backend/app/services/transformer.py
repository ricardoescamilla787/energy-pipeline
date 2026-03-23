import pandas as pd


def transform_outages(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia y estandariza el DataFrame crudo."""
    df = df.copy()
    df["period"] = pd.to_datetime(df["period"])

    # Renombrar a snake_case
    df = df.rename(columns={"percentOutage": "percent_outage"})

    # Descartar filas con valores nulos en métricas
    df = df.dropna(subset=["capacity", "outage", "percent_outage"])

    return df[["period", "capacity", "outage", "percent_outage"]].reset_index(drop=True)


def create_aggregations(df: pd.DataFrame) -> pd.DataFrame:
    """Genera estadísticas anuales desde el DataFrame limpio."""
    df = df.copy()
    df["year"] = pd.to_datetime(df["period"]).dt.year

    pct_col = "percent_outage" if "percent_outage" in df.columns else "percentOutage"

    stats = df.groupby("year").agg(
        avg_outage_mw      = ("outage",  "mean"),
        avg_percent_outage = (pct_col,   "mean"),
        max_outage_mw      = ("outage",  "max"),
        min_outage_mw      = ("outage",  "min"),
        record_count       = ("outage",  "count"),
    ).reset_index()

    return stats.round(2)
