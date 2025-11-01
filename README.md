# Digital-Investment-Analytics

Advanced medium to long-term investment analytics using deep learning and ML models.

## 🎯 Features

- Fetch US stock market data (prices + fundamentals)
- Feature engineering for ML models
- Multiple ML/DL model implementations
- Evaluation and backtesting tools

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/tedgt97/Digital-Investment-Analytics.git
cd Digital-Investment-Analytics
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

**Option A: Using pip**
```bash
pip install -r requirements.txt
```

**Option B: Editable install (recommended for development)**
```bash
pip install -e .
```

**Option C: With ML dependencies**
```bash
pip install -e ".[ml,dev]"
```

### 4. Configure API Key

1. Get free API key from [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs)
2. Create `config/api_keys.txt` with:
   ```
   FMP_API_KEY=your_actual_key_here
   ```

## 🚀 Quick Start

```python
from src.fmp_client import FMPClient

# Initialize client
client = FMPClient()

# Get stock data
prices = client.get_historical_prices('AAPL', '2020-01-01', '2024-12-31')
fundamentals = client.get_income_statement('AAPL')

print(prices.head())
```

## 📊 Project Structure

```
Digital-Investment-Analytics/
├── src/                    # Source code
│   ├── config.py          # Configuration management
│   ├── fmp_client.py      # API client
│   └── __init__.py
├── examples/              # Example scripts
├── tests/                 # Unit tests
├── data/                  # Data storage
│   ├── raw/              # Raw API data
│   └── processed/        # Cleaned data
├── models/               # Saved ML models
├── notebooks/            # Jupyter notebooks
└── config/               # Configuration files

```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT License

## 👤 Author

Your Name - [GitHub](https://github.com/tedgt97)