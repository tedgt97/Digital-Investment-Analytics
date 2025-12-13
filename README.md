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

Most day-to-day experimentation is done in notebooks first; the terminal/CLI is best suited for future bulk downloads once you have a higher API limit. 

```python
from fmp.client import FMPClient  

# Initialize client
client = FMPClient()

# Get stock data
prices = client.get_chart("AAPL", "2020-01-01", "2024-12-31")  
fundamentals = client.get_income_statement("AAPL")

print(prices.head())
```

### CLI usage (optional, via terminal) 

After installing in editable mode (`pip install -e .`), you can run the FMP CLI from the project root:

```bash
python -m fmp.tools.fmp_cli quote --symbol AAPL  
python -m fmp.tools.fmp_cli chart --symbol AAPL --from 2024-01-01 --to 2024-01-31  
```

Because the free FMP API key has strict limits, the CLI is currently best for small batches; large multi-symbol runs are an ideal future plan once higher limits are available. 

## API Plan Limitations 

The current setup assumes the FMP free tier. Symbol coverage depends on your plan: 

- **Free**: Symbol access limited to the following tickers: AAPL, TSLA, AMZN, MSFT, NVDA, GOOGL, META, NFLX, JPM, V, BAC, PYPL, DIS, T, PFE, COST, INTC, KO, TGT, NKE, SPY, BA, BABA, XOM, WMT, GE, CSCO, VZ, JNJ, CVX, PLTR, SQ, SHOP, SBUX, SOFI, HOOD, RBLX, SNAP, AMD, UBER, FDX, ABBV, ETSY, MRNA, LMT, GM, F, LCID, CCL, DAL, UAL, AAL, TSM, SONY, ET, MRO, COIN, RIVN, RIOT, CPRX, VWO, SPYG, NOK, ROKU, VIAC, ATVI, BIDU, DOCU, ZM, PINS, TLRY, WBA, MGM, NIO, C, GS, WFC, ADBE, PEP, UNH, CARR, HCA, TWTR, BILI, SIRI, FUBO, RKT. 
- **Starter**: Symbols limited to US exchanges. 
- **Premium**: Symbols limited to US, UK, and Canada exchanges. 

## 📊 Project Structure

```
Digital-Investment-Analytics/
├── src/                    # Source code (Python package root)
│   ├── fmp/               # FMP integration package 
│   │   ├── config.py      # FMP API key loading from config/api_keys.txt 
│   │   ├── client.py      # FMP API client (FMPClient) 
│   │   └── tools/         # CLI entrypoints (e.g., fmp_cli.py) 
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