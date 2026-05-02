"""
FRED Configuration Manager for Digital-Investment-Analytics

This module handles loading API keys and configuration settings.
It keeps sensitive information separate from code.
"""

from pathlib import Path

class Config:
    """
    Configuration class to manage API keys and settings.
    - Centralizes all configuration in one place
    - Makes it easy to switch between development/production
    - Keeps secrets out of main code
    """

    def __init__(self):
        # Get the project root directory (repository root, one level above src)
        self.project_root = Path(__file__).resolve().parents[2]
        self.config_file = self.project_root / 'config' / 'api_keys.txt'

        # Load API keys
        self.fred_api_key = self._load_api_key()
    
    def _load_api_key(self):
        """
        Private method to read API key from file

        Returns:
            str: My FRED API key

        Raises:
            FileNotFoundError: If api_keys.txt doesn't exist
            ValueErrorL: If API key is not set
        """
        try:
            if not self.config_file.exists():
                raise FileNotFoundError(
                    f"API keys file not found at: {self.config_file}\n"
                    f"Please create it suing the template."
                )
        
            # Read the file
            with open(self.config_file, 'r') as f:
                lines = f.readlines()

            # Parse the file (skip comments and empty lines)
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('FRED_API_KEY='):
                        api_key = line.split('=')[1].strip()

                        return api_key
            
            raise ValueError("FRED_API_KEY not found in config file.")
        
        except Exception as e:
            print(f" Error loading API key: {str(e)}")
            raise
    
    def get_api_key(self):
        """
        Public method to get the API key
        Returns:
            str: My FRED API key
        """
        return self.fred_api_key
    
    def __repr__(self):
        """String representation (hides the actual key)"""
        masked_key = self.fred_api_key[:4] + '....' + self.fred_api_key[-4:] if self.fred_api_key else 'Not set'
        return f"Config(FRED_API_KEY={masked_key})"


# Create a global config instance
config = Config()
