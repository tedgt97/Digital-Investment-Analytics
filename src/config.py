"""
Configuration Manager for Digital-Investment-Analytics

This module handles loading API keys and configuration settings.
It keeps sensitive information separate from code.
"""

import os
from pathlib import Path

class Config:
    """
    Configuration class to manage API keys and settings.
    - Centralizes all configuration in one place
    - Makes it easy to switch between development/production
    - Keeps secrets out of main code
    """

    def __init__(self):
        # Get the project rook directory
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / 'config' / 'api_keys.txt'

        # Load API keys
        self.fmp_api_key = self._load_api_key()
    
    def _load_api_key(self):
        """
        Private method to read API key from file

        Returns:
            str: My FMP API key
        
        Raises:
            FileNotFoundError: If api_keys.txt doesn't exist
            ValueError: If API key is not set
        """
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(
                    f"API keys file not found at: {self.config_file}\n"
                    f"Please create it using the template."
                )
            
            # Read the file
            with open(self.config_file, 'r') as f:
                lines = f.readlines()
            
            # Parse the file (skip comments and empty lines)
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('FMP_API_KEY='):
                        api_key = line.split('=')[1].strip()

                        return api_key
            
            raise ValueError("FMP_API_KEY not found in config file.")
        
        except Exception as e:
            print(f" Error loading API key: {str(e)}")
            raise

    def get_api_key(self):
        """
        Public method to get the API key
        Returns:
            str: My FMP API key
        """
        return self.fmp_api_key
    
    def __repr__(self):
        """String representation (hides the actual key)"""
        masked_key = self.fmp_api_key[:4] + '...' + self.fmp_api_key[-4:] if self.fmp_api_key else 'Not set'
        return f"Config(FMP_API_KEY={masked_key})"
    
# Create a global config instance
config = Config()