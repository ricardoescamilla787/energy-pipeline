"""
Tests de los endpoints del API.
Uso: cd backend && pytest tests/test_api.py -v
"""
import sys
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import app


@pytest.fixture
def client():
    """Cliente de prueba de Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "period":         pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "capacity":       [100000.0] * 3,
        "outage":         [5000.0, 4800.0, 7000.0],
        "percent_outage": [5.0, 4.8, 7.0],
    })


# /data 

def test_data_empty_when_no_parquet(client):
    with patch("api.load_outages", return_value=pd.DataFrame()):
        response = client.get("/data")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 0
    assert data["data"] == []

def test_data_returns_records(client, sample_df):
    with patch("api.load_outages", return_value=sample_df):
        response = client.get("/data")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 3
    assert len(data["data"]) == 3

def test_data_filter_by_date(client, sample_df):
    with patch("api.load_outages", return_value=sample_df):
        response = client.get("/data?date_from=2024-01-02")
    data = response.get_json()
    assert data["total"] == 2

def test_data_filter_by_min_outage(client, sample_df):
    with patch("api.load_outages", return_value=sample_df):
        response = client.get("/data?min_outage=6000")
    data = response.get_json()
    assert data["total"] == 1

def test_data_pagination(client, sample_df):
    with patch("api.load_outages", return_value=sample_df):
        response = client.get("/data?limit=2&page=1")
    data = response.get_json()
    assert len(data["data"]) == 2
    assert data["pages"] == 2


# /refresh 

def test_refresh_success(client):
    mock_result = {"status": "success", "records": 10}
    with patch("api.run_pipeline", return_value=mock_result):
        response = client.post("/refresh")
    assert response.status_code == 200
    assert response.get_json()["pipeline"]["status"] == "success"

def test_refresh_returns_error_on_failure(client):
    with patch("api.run_pipeline", side_effect=Exception("API key inválida")):
        response = client.post("/refresh")
    assert response.status_code == 500
    assert "error" in response.get_json()["status"]
