import os
import logging
import pandas as pd
from app.config import DATA_PATH

def get_last_period():
    if not os.path.exists(DATA_PATH):
        return None

    df = pd.read_parquet(DATA_PATH)

    if df.empty or "period" not in df.columns:
        return None

    return df["period"].max()

def save_parquet(df: pd.DataFrame):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

    df["period"] = pd.to_datetime(df["period"])

    if os.path.exists(DATA_PATH):
        existing_df = pd.read_parquet(DATA_PATH)
        existing_df["period"] = pd.to_datetime(existing_df["period"])
        df = pd.concat([existing_df, df])
        df = df.drop_duplicates(subset=["period"])

    df = df.sort_values("period")
    df["period"] = pd.to_datetime(df["period"])

    df.to_parquet(DATA_PATH, index=False)

def save_transformed(outages_df, stats_df):
    outages_df.to_parquet("data/outages_clean.parquet", index=False)
    stats_df.to_parquet("data/outage_stats.parquet", index=False)