"""
Alpha Vantage API Client

This is the main interface to fetch financial data from Alpha Vantage.
"""

from typing import Any, Dict, List, Optional, cast
import time

import pandas as pd
import requests

from .config import config

class AlphaVantageClient:
    """Client for interacting with the Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        self.api_key = api_key or config.get_api_key()
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Digital-Investment-Analytics/0.2.2"}
        )

        if self.verbose:
            print("Alpha Vantage Client initialized")

    def _make_request(self, function: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Internal method to make Alpha Vantage API requests with error handling."""
        request_params: Dict[str, str] = dict(params or {})

        request_params["function"] = function
        request_params["apikey"] = self.api_key

        try:
            response = self.session.get(self.BASE_URL, params=request_params, timeout=30)
            response.raise_for_status()
            payload = response.json()

            if not isinstance(payload, dict):
                raise Exception(f"Unexpected response format for {function}")
            
            data = cast(Dict[str, Any], payload)

            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Information" in data:
                raise Exception(f"Alpha Vantage info: {data['Information']}")
            if "Note" in data:
                raise Exception(f"Alpha Vantage rate limit: {data['Note']}")
            
            time.sleep(1.2)
            return data
    

        except requests.exceptions.HTTPError as e:  
            status_code = getattr(getattr(e, "response", None), "status_code", None)  
            if status_code is not None:  
                raise Exception(f"HTTP Error {status_code}: {str(e)}")  
            raise Exception(f"HTTP Error: {str(e)}")  
        except requests.exceptions.Timeout:  
            raise Exception(f"Request timeout for {function}")  
        except requests.exceptions.ConnectionError:  
            raise Exception("Connection error - check internet connection")  
        except Exception as e:  
                raise Exception(f"Request failed for {function}: {str(e)}")  
        
    

    def get_gold_silver_history(
            self,
            symbol: str = "GOLD",
            interval: str = "daily",
    ) -> pd.DataFrame:
        """Get historical gold/silver prices."""
        normalized_symbol = symbol.upper()
        normalized_interval = interval.lower()
        data = self._make_request(
            "GOLD_SILVER_HISTORY",
            {"symbol": normalized_symbol, "interval": normalized_interval}
        )
        rows = cast(List[Dict[str, Any]], data.get("data", []))
        if not rows:
            raise Exception(f"No gold/silver history found for symbol={normalized_symbol}, interval={normalized_interval}")
        
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["symbol"] = normalized_symbol
        df["interval"] = normalized_interval
        df["nominal"] = data.get("nominal")
        return df.sort_values("date").reset_index(drop=True)
    
    def get_gold_silver_spot(self, symbol: str = "GOLD") -> Dict[str, Any]:
        """Get live gold/silver spot price."""
        normalized_symbol = symbol.upper()
        data = self._make_request(
            "GOLD_SILVER_SPOT",
            {"symbol": normalized_symbol},
        )
        if "price" not in data:
            raise Exception(f"No spot price found for symbol={normalized_symbol}")
        data["symbol"] = normalized_symbol
        return data
    