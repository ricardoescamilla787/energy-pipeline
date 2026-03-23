"""
Tests del modelo de datos (Part 2).
Uso: cd backend && pytest tests/test_parquet.py -v
"""
import sys
import pytest
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.model import build_outages_table, build_stats_table


@pytest.fixture
def raw_df():
    return pd.DataFrame({
        "period":        pd.to_datetime(["2023-06-01", "2023-06-02", "2024-01-01", "2024-01-02"]),
        "capacity":      [100000.0] * 4,
        "outage":        [5000.0, 4800.0, 6000.0, 5800.0],
        "percentOutage": [5.0, 4.8, 6.0, 5.8],
    })


# Tests: outages_table 

def test_outages_columns(raw_df):
    result = build_outages_table(raw_df)
    assert list(result.columns) == ["period", "capacity", "outage", "percent_outage"]

def test_outages_no_duplicates(raw_df):
    result = build_outages_table(raw_df)
    assert result["period"].duplicated().sum() == 0

def test_outages_row_count(raw_df):
    result = build_outages_table(raw_df)
    assert len(result) == 4


# Tests: stats_table 

def test_stats_columns(raw_df):
    result = build_stats_table(raw_df)
    expected = ["year", "avg_outage_mw", "avg_percent_outage",
                "max_outage_mw", "min_outage_mw", "total_records"]
    assert list(result.columns) == expected

def test_stats_years(raw_df):
    result = build_stats_table(raw_df)
    assert sorted(result["year"].tolist()) == [2023, 2024]

def test_stats_total_records(raw_df):
    result = build_stats_table(raw_df)
    assert result["total_records"].sum() == 4
