"""
Federal Reserve Bank of ST. Louis API Client

This is the main interface to fetch core macroeconomic data from FRED.
"""

from typing import Dict, Optional
import time

import pandas as pd
import requests

from .config import config

class FREDClient:
    """ Client for interacting with the FRED API."""

    BASE_URL = "https://api.stlouisfed.org/fred"

    def __init__(self, api_key: Optional[str] = None, verbose: bool = True):
        self.api_key = api_key or config.get_api_key()
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Digital-Investment_Analytics"}
        )

        if self.verbose:
            print("FRED Client initialized")
        
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> Dict:
        """Internal method to make FRED API requests with error handling."""
        if params is None:
            params = {}

        params["api_key"] = self.api_key
        params["file_type"] = "json"

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "error_code" in data:
                raise Exception(
                    f"FRED API Error {data['error_code']}: "
                    f"{data.get('error_message', 'Unknown error')}"
                )
            
            time.sleep(0.25)
            return data
        
        except requests.exceptions.HTTPError as e:  
            status_code = getattr(getattr(e, "response", None), "status_code", None)  
            if status_code is not None:  
                raise Exception(f"HTTP Error {status_code}: {str(e)}")  
            raise Exception(f"HTTP Error: {str(e)}")  
        except requests.exceptions.Timeout:  
            raise Exception(f"Request timeout for {endpoint}")  
        except requests.exceptions.ConnectionError:  
            raise Exception("Connection error - check internet connection")  
        except Exception as e:  
            raise Exception(f"Request failed for {endpoint}: {str(e)}")  
        
    def get_series(self, series_id: str) -> Dict:
        """Get metadata for a FRED series."""
        data = self._make_request("/series", {"series_id": series_id})
        series_list = data.get("seriess", [])
        if not series_list:
            raise Exception(f"No series metadata found for {series_id}")
        return series_list[0]
    
    def get_series_observations(
            self,
            series_id: str,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            frequency: Optional[str] = None,
            aggregation_method: Optional[str] = None,
    ) -> pd.DataFrame:
        """Get time-series observations for a FRED series."""
        params = {"series_id": series_id}

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
        if frequency:
            params["frequency"] = frequency
        if aggregation_method:
            params["aggregation_method"] = aggregation_method
        
        data = self._make_request("/series/observations", params)
        observations = data.get("observations", [])

        if not observations:
            raise Exception(f"No observations found for {series_id}")
        
        df = pd.DataFrame(observations)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.sort_values("date").reset_index(drop=True)

