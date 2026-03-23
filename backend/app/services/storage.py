import io
import os
import logging
import pandas as pd
from app.config import (
    RAW_PATH, CLEAN_PATH, STATS_PATH,
    SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET,
    USE_CLOUD
)

# Cliente de Supabase
def _get_supabase():
    """Retorna el cliente de Supabase."""
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# Helpers de Supabase 
def _upload_parquet(df: pd.DataFrame, filename: str):
    """Sube un DataFrame como archivo Parquet a Supabase Storage."""
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    supabase = _get_supabase()
    supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=filename,
        file=buffer.getvalue(),
        file_options={"content-type": "application/octet-stream", "upsert": "true"}
    )

def _download_parquet(filename: str) -> pd.DataFrame | None:
    """Descarga un archivo Parquet desde Supabase Storage."""
    try:
        supabase = _get_supabase()
        data = supabase.storage.from_(SUPABASE_BUCKET).download(filename)
        return pd.read_parquet(io.BytesIO(data))
    except Exception:
        return None

 
def _ensure_dir(path):
    """Crea el directorio local si no existe."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

 
def get_last_period():
    """Devuelve el período más reciente guardado. Retorna None si no hay datos previos."""
    if USE_CLOUD:
        df = _download_parquet("outages_raw.parquet")
        if df is None or df.empty:
            return None
        return pd.to_datetime(df["period"]).max()
    else:
        if not os.path.exists(RAW_PATH):
            return None
        df = pd.read_parquet(RAW_PATH, columns=["period"])
        if df.empty:
            return None
        return pd.to_datetime(df["period"]).max()


def save_raw(df: pd.DataFrame):
    """Guarda el DataFrame crudo en Parquet, combinando con datos existentes."""
    df = df.copy()
    df["period"] = pd.to_datetime(df["period"])

    if USE_CLOUD:
        existing = _download_parquet("outages_raw.parquet")
        if existing is not None:
            existing["period"] = pd.to_datetime(existing["period"])
            df = pd.concat([existing, df]).drop_duplicates(subset=["period"])
        df = df.sort_values("period").reset_index(drop=True)
        _upload_parquet(df, "outages_raw.parquet")
    else:
        _ensure_dir(RAW_PATH)
        if os.path.exists(RAW_PATH):
            existing = pd.read_parquet(RAW_PATH)
            existing["period"] = pd.to_datetime(existing["period"])
            df = pd.concat([existing, df]).drop_duplicates(subset=["period"])
        df = df.sort_values("period").reset_index(drop=True)
        df.to_parquet(RAW_PATH, index=False)

    logging.info(f"Datos crudos guardados: {len(df)} registros")


def save_transformed(clean_df: pd.DataFrame, stats_df: pd.DataFrame):
    """Guarda los DataFrames transformados en archivos separados."""
    if USE_CLOUD:
        _upload_parquet(clean_df, "outages_clean.parquet")
        _upload_parquet(stats_df, "outage_stats.parquet")
    else:
        _ensure_dir(CLEAN_PATH)
        _ensure_dir(STATS_PATH)
        clean_df.to_parquet(CLEAN_PATH, index=False)
        stats_df.to_parquet(STATS_PATH, index=False)

    logging.info(f"Datos limpios guardados: {len(clean_df)} registros")
    logging.info(f"Estadísticas guardadas: {len(stats_df)} registros")


def load_clean() -> pd.DataFrame:
    """Carga el parquet de outages limpios."""
    if USE_CLOUD:
        df = _download_parquet("outages_clean.parquet")
        return df if df is not None else pd.DataFrame()
    else:
        if not os.path.exists(CLEAN_PATH):
            return pd.DataFrame()
        return pd.read_parquet(CLEAN_PATH)


def load_stats() -> pd.DataFrame:
    """Carga el parquet de estadísticas anuales."""
    if USE_CLOUD:
        df = _download_parquet("outage_stats.parquet")
        return df if df is not None else pd.DataFrame()
    else:
        if not os.path.exists(STATS_PATH):
            return pd.DataFrame()
        return pd.read_parquet(STATS_PATH)
