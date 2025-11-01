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
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    BASE_URL_V4 = "https://financialmodelingprep.com/api/v4"

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
            'User-Agent': 'Stock-Predictor/0.1.0'
        })

        if self.verbose:
            print(f"FMP Client initialized")
            print("Daily request limit: {self.daily_limit}")

    def _make_request(
            self, 
            endpoint: str, 
            params: Optional[Dict] = None, 
            base_url: Optional[str] = None
            ) -> Union[Dict, List]:
        """
        Internal method to make API requests with error handling

        Args:
            endpoint: API endpoint (e.g., '/quote/AAPL')
            params: Additional URL parameters
            base_url: Override default base URL (for v4 endpoints)
        
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
            
            