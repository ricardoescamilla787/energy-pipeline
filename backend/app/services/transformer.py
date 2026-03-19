import pandas as pd

def transform_outages(df: pd.DataFrame):
    df = df.copy()

    # Crear ID
    df["outage_id"] = range(1, len(df) + 1)

    # Renombrar columna para consistencia
    df = df.rename(columns={"percentOutage": "percent_outage"})

    outages = df[[
        "outage_id",
        "period",
        "capacity",
        "outage",
        "percent_outage"
    ]]

    return outages


def create_aggregations(df: pd.DataFrame):
    df = df.copy()

    df["year"] = df["period"].dt.year

    stats = df.groupby("year").agg({
        "outage": "mean",
        "percentOutage": "mean"
    }).reset_index()

    stats = stats.rename(columns={
        "outage": "avg_outage",
        "percentOutage": "avg_percent_outage"
    })

    return stats