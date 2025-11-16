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
    assert quote['symbol'] == 'AAPL'

def test_get_chart():
    """Test getting chart data"""
    client = FMPClient(verbose=False)
    df = client.get_chart('AAPL', '2024-01-01', '2024-01-31')
    assert isinstance(df, pd.DataFrame)
    assert 'date' in df.columns
    assert 'close' in df.columns
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'volume' in df.columns
    assert 'change' in df.columns
    assert 'changePercent' in df.columns
    assert 'vwap' in df.columns
    assert len(df) > 0

def test_get_income_statement():
    """Test getting income statement data"""
    client = FMPClient(verbose=False)
    df = client.get_income_statement('AAPL', period='annual', limit=3)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert 'revenue' in df.columns or 'totalRevenue' in df.columns
    # Income statements should have at least 1 year of data
    assert len(df) >= 1

def test_get_company_profile():
    """Test getting company profile"""
    client = FMPClient(verbose=False)
    profile = client.get_company_profile('AAPL')
    assert isinstance(profile, dict)
    assert 'symbol' in profile
    assert profile['symbol'] == 'AAPL'
    assert 'companyName' in profile
    assert 'industry' in profile
    assert 'sector' in profile

# def test_get_stock_list():
#     """Test getting list of symbols"""
#     client = FMPClient(verbose=False)
#     profile = client.get_stock_list()
#     assert isinstance(profile, list)
#     assert len(profile) > 0

# def test_get_multiple_quotes():
#     """Test getting multiple quotes at once"""
#     client = FMPClient(verbose=False)
#     symbols = ['AAPL', 'MSFT', 'GOOGL']
#     df = client.get_multiple_quotes(symbols)
#     assert isinstance(df, pd.DataFrame)
#     assert len(df) == 3
#     assert 'symbol' in df.columns
#     assert 'price' in df.columns
#     # Check all symbols are present
#     assert set(df['symbol'].tolist()) == set(symbols)


### Test error handling
def test_invalid_symbol():
    """Test handling of invalid stock symbol"""
    client = FMPClient(verbose=False)
    with pytest.raises(Exception):
        client.get_quote('INVALID_SYMBOL_XYZ123')

def test_invalid_date_range():
    """Test handling of invalid date range"""
    client = FMPClient(verbose=False)
    with pytest.raises(Exception):
        # Future dates should fail
        client.get_historical_prices('AAPL', '2030-01-01', '2030-12-31')
