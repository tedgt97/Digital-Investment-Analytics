"""
Financial Modeling Prep API Client

This is the main interface to fetch stock data from FMP.
It wraps all API calls in easy-to-use Python functions.

Usage:
    from fmp.client import FMPClient  # --Added--

    client = FMPClient()
    prices = client.get_chart("AAPL", "2020-01-01", "2024-12-31")
    fundamentals = client.get_income_statement("AAPL")
"""

import requests
import pandas as pd
from typing import List, Dict, Optional, Union
import time
import warnings

from .config import config
from .usage import FMPUsageTracker


class FMPClient:
    """Client for interacting with Financial Modeling Prep API."""

    BASE_URL = "https://financialmodelingprep.com/stable"

    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        """Initialize the FMP client."""
        self.api_key = api_key or config.get_api_key()
        self.verbose = verbose
        self.usage_tracker = FMPUsageTracker()
        self.request_count = self.usage_tracker.count
        self.daily_limit = 250  # Free tier limit

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Digital-Investment-Analytics/0.1.0"})

        if self.verbose:
            print("FMP Client initialized")
            print(f"Daily request limit: {self.daily_limit}")

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        base_url: Optional[str] = None,
    ) -> Union[Dict, List]:
        """Internal method to make API requests with error handling."""
        if params is None:
            params = {}

        params["apikey"] = self.api_key

        if self.request_count >= self.daily_limit:
            warnings.warn(f"Daily limit of {self.daily_limit} requests reached.")

        url = f"{base_url or self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=30)

            self.request_count += 1
            self.usage_tracker.increment()
            if self.verbose:
                print(f"Request {self.request_count}/{self.daily_limit}: {endpoint}")

            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "Error Message" in data:
                raise Exception(f"FMP API Error: {data['Error Message']}")

            time.sleep(0.25)

            return data

        except requests.exceptions.HTTPError as e:
            status_code = getattr(getattr(e, "response", None), "status_code", None)  # --Fixed--
            if status_code is not None:  # --Added--
                raise Exception(f"HTTP Error {status_code}: {str(e)}")  # --Fixed--
            raise Exception(f"HTTP Error: {str(e)}")  # --Fixed--
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout for {endpoint}")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error - check internet connection")
        except Exception as e:
            raise Exception(f"Request failed for {endpoint}: {str(e)}")
        
    # Monitoring Request Usage
    def get_request_usage(self) -> Dict[str, int]:
        """Return current request usage and remaining quota for this FMP daily window."""
        remaining = self.usage_tracker.remaining(self.daily_limit)
        return {
            'used': self.request_count,
            'limit': self.daily_limit,
            'remaining': remaining
        }


    def get_chart(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get full price and volume data for a stock."""
        endpoint = f"/historical-price-eod/full?symbol={symbol}"
        params = {"from": start_date, "to": end_date}

        data = self._make_request(endpoint, params)
        if not data:
            raise Exception(f"No chart data found for {symbol}")

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    def get_historical_prices(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Alias for get_chart (kept for backwards compatibility)."""  # --Added--
        return self.get_chart(symbol, start_date, end_date)  # --Added--

    def get_quote(self, symbol: str) -> Dict:
        """Get real-time stock quote."""
        endpoint = f"/quote?symbol={symbol}"
        data = self._make_request(endpoint)

        if not data:
            raise Exception(f"No quote data found for {symbol}")

        return data[0] if isinstance(data, list) else data

    def get_income_statement(
        self,
        symbol: str,
        period: str = "annual",
        limit: int = 5,
    ) -> pd.DataFrame:
        """Get income statement data."""
        endpoint = f"/income-statement?symbol={symbol}"
        params = {"period": period, "limit": limit}

        data = self._make_request(endpoint, params)
        if not data:
            raise Exception(f"No income statement data found for {symbol}")

        df = pd.DataFrame(data)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df

    def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile information."""
        endpoint = f"/profile?symbol={symbol}"
        data = self._make_request(endpoint)

        if not data:
            raise Exception(f"No profile found for {symbol}")

        return data[0] if isinstance(data, list) else data

    # The following endpoints are not available for the free tier but left
    # as references for future extension. # --Added--

    # def get_stock_list(self) -> pd.DataFrame:
    #     """Get a comprehensive list of financial symbols."""
    #     endpoint = "/stock-list"
    #     data = self._make_request(endpoint)
    #     if not data:
    #         raise Exception("No stock list data found")
    #     return pd.DataFrame(data)

    # def get_multiple_quotes(self, symbols: List[str]) -> pd.DataFrame:
    #     """Get quotes for multiple stocks at once."""
    #     symbols_str = ",".join(symbols)
    #     endpoint = f"/quote?symbol={symbols_str}"
    #     data = self._make_request(endpoint)
    #     return pd.DataFrame(data)
