"""
Tests del conector y pipeline.
Uso: cd backend && pytest tests/test_connector.py -v
"""
import sys
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.extractor  import fetch_outages
from app.services.pipeline   import run_pipeline
from app.utils.http_client   import get_with_retry


# Fixtures 

@pytest.fixture
def sample_records():
    return [
        {"period": "2024-01-01", "capacity": "100000", "outage": "5000", "percentOutage": "5.0"},
        {"period": "2024-01-02", "capacity": "100000", "outage": "4800", "percentOutage": "4.8"},
        {"period": "2024-01-03", "capacity": "100000", "outage": "5200", "percentOutage": "5.2"},
    ]

@pytest.fixture
def api_page(sample_records):
    return {"response": {"data": sample_records}}

@pytest.fixture
def empty_page():
    return {"response": {"data": []}}


# Tests: extractor 

def test_fetch_raises_without_api_key():
    with patch("app.services.extractor.API_KEY", None):
        with pytest.raises(Exception, match="EIA_API_KEY no encontrada"):
            fetch_outages()

def test_fetch_returns_records(api_page, empty_page):
    with patch("app.services.extractor.API_KEY", "fake-key"), \
         patch("app.services.extractor.get_with_retry", side_effect=[api_page, empty_page]):
        result = fetch_outages()
    assert len(result) == 3

def test_fetch_paginates(api_page, empty_page):
    with patch("app.services.extractor.API_KEY", "fake-key"), \
         patch("app.services.extractor.get_with_retry", side_effect=[api_page, api_page, empty_page]):
        result = fetch_outages()
    assert len(result) == 6


# Tests: http_client 

def test_raises_on_401():
    mock_response = MagicMock()
    mock_response.status_code = 401
    with patch("app.utils.http_client.requests.get", return_value=mock_response):
        with pytest.raises(Exception, match="API Key inválida"):
            get_with_retry("https://fake.url", {})

def test_retries_on_network_error():
    import requests as req
    with patch("app.utils.http_client.requests.get", side_effect=req.exceptions.ConnectionError()), \
         patch("app.utils.http_client.time.sleep"):
        with pytest.raises(Exception, match="No se pudo conectar"):
            get_with_retry("https://fake.url", {})


# Tests: pipeline 

def test_pipeline_success(sample_records):
    with patch("app.services.pipeline.fetch_outages", return_value=sample_records), \
         patch("app.services.pipeline.get_last_period", return_value=None), \
         patch("app.services.pipeline.save_raw"), \
         patch("app.services.pipeline.save_transformed"):
        result = run_pipeline()
    assert result["status"] == "success"
    assert result["records"] == 3

def test_pipeline_up_to_date(sample_records):
    with patch("app.services.pipeline.fetch_outages", return_value=sample_records), \
         patch("app.services.pipeline.get_last_period", return_value=pd.Timestamp("2024-12-31")):
        result = run_pipeline()
    assert result["status"] == "up_to_date"
