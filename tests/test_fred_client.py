"""Tests for FRED Client"""

import pandas as pd
import pytest

from fred.client import FREDClient

def test_client_initialization():
    """Test that client initializes correctly"""
    client = FREDClient(verbose=False)
    assert client.api_key is not None
    assert client.BASE_URL == "https://api.stlouisfed.org/fred"

def test_get_series():
    """Test getting FRED series metadata."""
    client = FREDClient(verbose=False)
    series = client.get_series("FEDFUNDS")

    assert isinstance(series, dict)
    assert series["id"] == "FEDFUNDS"
    assert "title" in series
    assert "frequency" in series

def test_get_series_observations():
    """Test getting FRED series observations."""
    client = FREDClient(verbose=False)
    df = client.get_series_observations("FEDFUNDS", "2024-01-01", "2024-12-31")

    assert isinstance(df, pd.DataFrame)
    assert "date" in df.columns
    assert "value" in df.columns
    assert len(df)
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_numeric_dtype(df["value"])

def test_invalid_series():
    """Test handling of an invalid FRED series id."""
    client = FREDClient(verbose=False)
    with pytest.raises(Exception):
        client.get_series("INVALID_SERIES_XYZ123")

