"""
Tests for FMP Client
"""
import pytest
import pandas as pd
from src.fmp_client import FMPClient

def test_client_initialization():
    """Test that client initializes correctly"""
    client = FMPClient(verbose=False)
    assert client.api_key is not None
    assert client.daily_limit == 250

def test_get_quote():
    """Test getting real-time quote"""
    client = FMPClient(verbose=False)
    quote = client.get_quote('AAPL')
    assert 'price' in quote
    assert 'symbol' in quote

def test_historical_prices():
    """Test getting historical data"""
    client = FMPClient(verbose=False)
    df = client.get_historical_prices('AAPL', '2024-01-01', '2024-01-31')
    assert isinstance(df, pd.DataFrame)
    assert 'date' in df.columns
    assert 'close' in df.columns
    assert len(df) > 0

