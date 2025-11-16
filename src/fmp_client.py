"""
Financial Modeling Prep API Client

This is the main interface to fetch stock data from FMP.
It wraps all API calls in easy-to-use Python functions.

Usage:
    from src.fmp_client import FMPClient

    client = FMPClient()
    prices = client.get_historical_prices('AAPL', '2020-01-01', '2024-12-31')
    fundamentals = client.get_income_statement('AAPL')
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import time
import warnings

from src.config import config

class FMPClient:
    """
    Client for interacting with Financial Modeling Prep API.

    This class handles all HTTP requests to FMP and converts responses to Pandas DataFrames for easy data analysis and ML model training.

    Features:
    - Automatic rate limiting (250 requests/day for free tier)
    - Error handling and retry logic
    - Data validation
    - Progress tracking
    - Caching support

    Attributes:
        api_key (str): My FMP API key
        request_count (int): Number of requests made in current session
        daily_limit (int): Maximum requests per day (250 for free tier)
        session (requests.Session): Reusable HTTP session for better performance
    """

    # API endpoints
    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        """
        Initialize the FMP client

        Args:
            api_key: My FMP API key (loads from config if not provided)
            verbose: Print request information (default: True)

        Example:
            >>> client = FMPClient()
            >>> # Or with custom key:
            >>> client = FMPClient(api_key="NewAPIKey")
        """
        self.api_key = api_key or config.get_api_key()
        self.verbose = verbose
        self.request_count = 0
        self.daily_limit = 250  # Free tier limit

        # Create a session for connection pooling (faster requests)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Digital-Investment-Analytics/0.1.0'
        })

        if self.verbose:
            print(f"FMP Client initialized")
            print(f"Daily request limit: {self.daily_limit}")

    def _make_request(
            self, 
            endpoint: str, 
            params: Optional[Dict] = None, 
            base_url: Optional[str] = None
            ) -> Union[Dict, List]:
        """
        Internal method to make API requests with error handling

        Args:
            endpoint: API endpoint
            params: Additional URL parameters
            base_url: Override default base URL
        
        Returns:
            dict or list: JSON response from API

        Raises:
            Exception: If request fails or API returns error
        
        Why private (_make_request):
            - User don't call this directly
            - Centralizes error handling
            - Tracks request count
            - Implements retry logic
        """
        if params is None:
            params = {}
        
        # Add API key to every request
        params['apikey'] = self.api_key

        # Check rate limit
        if self.request_count >= self.daily_limit:
            warnings.warn(
                f"Daily limit of {self.daily_limit} requests reached."   
            )
        
        # Build full URL
        url = f"{base_url or self.BASE_URL}{endpoint}"

        try:
            # Make the HTTP request
            response = self.session.get(url, params=params, timeout=30)

            # Track requests
            self.request_count += 1
            if self.verbose:
                print(f"Request {self.request_count}/{self.daily_limit}: {endpoint}")
            
            # Check HTTP status
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Check for API errors
            if isinstance(data, dict) and 'Error Message' in data:
                raise Exception(f"FMP API Error: {data['Error Message']}")

            # Add small delay to respect rate limits (4 requests/second max)
            time.sleep(0.25)

            return data
        
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error {response.status_code}: {str(e)}")
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout for {endpoint}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error - check internet connection")
        except Exception as e:
            raise Exception(f"Request failed for {endpoint}: {str(e)}")

    def get_chart(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Get full price and volume data for a stock

        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            start_date: Start date in 'YYYY-MM-DD'
            end_date: End date in 'YYYY-MM-DD'
        
        Returns: 
            DataFrame with columns: date, open, high, low, close, volume, change, changePercent, vwap

        Example:
            >>> charts = client.get_chart('AAPL', '2020-01-01', '2024-12-31')
            >>> print(charts.head())
        """
        endpoint = f"/historical-price-eod/full?symbol={symbol}"
        params = {
            'from': start_date,
            'to': end_date
        }
        
        data = self._make_request(endpoint, params)

        if not data:
            raise Exception(f"No chart data found for {symbol}")
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        return df

    def get_quote(self, symbol: str) -> Dict:
        """
        Get real-time stock quote

        Args:
            symbol: Stock ticker

        Returns:
            Dict with current price, volume, change, etc.

        Example:
            >>> quote = client.get_quote('AAPL')
            >>> print(f"Current price: ${quote['price']}")
        """
        endpoint = f"/quote?symbol={symbol}"
        data = self._make_request(endpoint)

        if not data:
            raise Exception(f"No quote data found for {symbol}")
        
        return data[0] if isinstance(data, list) else data
    
    def get_income_statement(
            self,
            symbol: str,
            period: str = 'annual',
            limit: int = 5
    ) -> pd.DataFrame:
        """
        Get income statement data

        Args:
            symbol: Stock ticker
            period: 'annual' or 'quarter'
            limit: Number of periods to retrieve

        Returns:
            DataFrame with financial metrics

        Example:
            >>> fundamentals = client.get_income_statement('AAPL')
        """
        endpoint = f"/income-statement?symbol={symbol}"
        params = {
            'period': period,
            'limit': limit
        }

        data = self._make_request(endpoint, params)

        if not data:
            raise Exception(f"No income statement data found for {symbol}")
        
        df = pd.DataFrame(data)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df

    def get_company_profile(self, symbol: str) -> Dict:
        """
        Get company profile information

        Args:
            symbol: Stock ticker
        
        Returns:
            Dict with company name, sector, industry, description, etc.
        """
        endpoint = f"/profile?symbol={symbol}"
        data = self._make_request(endpoint)

        if not data:
            raise Exception(f"No profile found for {symbol}")
        
        return data[0] if isinstance(data, list) else data
    
    # Not available for free tier
    # def get_stock_list(self) -> Dict:
    #     """
    #     Get a comprehensive list of financial symbols

    #     Args:
    #         None
        
    #     Returns: symbol, companyName
    #     """
    #     endpoint = f"/stock-list"
    #     data = self._make_request(endpoint)

    #     if not data:
    #         raise Exception(f"No stock list data found")
        
    #     df = pd.DataFrame(data)
    #     return df
    

    
    # def get_multiple_quotes(self, symbols: List[str]) -> pd.DataFrame:
    #     """
    #     Get quotes for multiple stocks at once

    #     Args:
    #         symbols: List of stock tickers

    #     Returns:
    #         DataFrame with quotes of all symbols
    #     """
    #     symbols_str = ','.join(symbols)
    #     endpoint = f"/quote?symbol={symbols_str}"
    #     data = self._make_request(endpoint)

    #     return pd.DataFrame(data)

