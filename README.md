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

Most day-to-day experimentation is done in notebooks first; the terminal/CLI is best suited for future bulk downloads once you have a higher API limit. # --Added--

```python
from fmp.client import FMPClient  # --Fixed--

# Initialize client
client = FMPClient()

# Get stock data
prices = client.get_chart("AAPL", "2020-01-01", "2024-12-31")  # --Fixed--
fundamentals = client.get_income_statement("AAPL")

print(prices.head())
```

### CLI usage (optional, via terminal) # --Added--

After installing in editable mode (`pip install -e .`), you can run the FMP CLI from the project root:

```bash
python -m fmp.tools.fmp_cli quote --symbol AAPL  # --Added--
python -m fmp.tools.fmp_cli chart --symbol AAPL --from 2024-01-01 --to 2024-01-31  # --Added--
```

Because the free FMP API key has strict limits, the CLI is currently best for small batches; large multi-symbol runs are an ideal future plan once higher limits are available. # --Added--

## 📊 Project Structure

```
Digital-Investment-Analytics/
├── src/                    # Source code (Python package root)
│   ├── fmp/               # FMP integration package # --Fixed--
│   │   ├── config.py      # FMP API key loading from config/api_keys.txt # --Added--
│   │   ├── client.py      # FMP API client (FMPClient) # --Added--
│   │   └── tools/         # CLI entrypoints (e.g., fmp_cli.py) # --Added--
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