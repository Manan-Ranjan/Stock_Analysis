# Stock Analysis Project

This folder contains all stock analysis related files and tools for analyzing Indian stock market data.

## 🆕 NEW: Multi-Source Data Fetching

Now supports **Google Finance** and **Yahoo Finance** with automatic fallback! See [README_DATA_SOURCES.md](README_DATA_SOURCES.md) for details.

## 📁 Folder Structure

```
StockAnalysis/
├── README.md                      # This file
├── data_fetcher.py                # 🆕 Multi-source data fetcher (Google + Yahoo)
├── data_source_config.json        # 🆕 Data source configuration
├── example_data_sources.py        # 🆕 Usage examples
├── README_DATA_SOURCES.md         # 🆕 Data sources documentation
├── hdfc_stock_analyzer.py         # HDFC Bank specific stock analyzer
├── multi_stock_analyzer.py        # Multi-stock portfolio analyzer
├── hdfc_bank_data.csv            # HDFC Bank historical data
├── hdfc_bank_trends.html         # HDFC Bank analysis report
├── multi_stock_trends.html       # Multi-stock analysis report
├── stocks_config.csv             # Configuration for multiple stocks
├── hdfc_requirements.txt         # Dependencies for HDFC analyzer
├── multi_stock_requirements.txt  # Dependencies for multi-stock analyzer
├── README_HDFC_ANALYZER.md       # Documentation for HDFC analyzer
├── README_MULTI_STOCK.md         # Documentation for multi-stock analyzer
└── stock_data/                   # Historical stock data directory
    ├── ADANIENT_data.csv
    ├── ADANIPOWER_data.csv
    ├── ASIANPAINT_data.csv
    ├── GAIL_data.csv
    ├── HDFCBANK_data.csv
    ├── HINDUNILVR_data.csv
    ├── ICICIBANK_data.csv
    ├── INFY_data.csv
    ├── IOC_data.csv
    ├── IRCTC_data.csv
    ├── ITC_data.csv
    ├── JIOFIN_data.csv
    ├── LT_data.csv
    ├── OIL_data.csv
    ├── PFC_data.csv
    ├── RELIANCE_data.csv
    ├── SAIL_data.csv
    ├── SBIN_data.csv
    ├── TATAMOTORS_data.csv
    ├── TATASTEEL_data.csv
    ├── TCS_data.csv
    └── VEDL_data.csv
```

## 🚀 Quick Start

### Option 1: Multi-Source Data Fetcher (Recommended)
```bash
pip install -r multi_stock_requirements.txt
python example_data_sources.py
```

### Option 2: HDFC Bank Analyzer
```bash
pip install -r hdfc_requirements.txt
python hdfc_stock_analyzer.py
```

### Option 3: Multi-Stock Analyzer
```bash
pip install -r multi_stock_requirements.txt
python multi_stock_analyzer.py
```

## 🔄 Data Sources

The system now supports multiple data sources with automatic fallback:

### **Google Finance** (Web Scraping)
- ✅ Real-time current prices
- ✅ No API key required
- ❌ Limited historical data

### **Yahoo Finance** (API)
- ✅ Extensive historical data
- ✅ Technical indicators
- ✅ Reliable and stable

**Usage Example:**
```python
from data_fetcher import DataFetcher

# Google primary, Yahoo fallback
fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)

# Get current price
price = fetcher.get_current_price('RELIANCE', 'NSE')
```

See [README_DATA_SOURCES.md](README_DATA_SOURCES.md) for complete documentation.

## 📊 Available Stock Data

The `stock_data/` directory contains historical data for 22 Indian stocks:
- Banking: HDFCBANK, ICICIBANK, SBIN
- IT: INFY, TCS
- Energy: GAIL, IOC, OIL, RELIANCE
- Industrials: LT, TATAMOTORS, TATASTEEL, SAIL
- Consumer: ASIANPAINT, HINDUNILVR, ITC
- Adani Group: ADANIENT, ADANIPOWER
- Others: IRCTC, JIOFIN, PFC, VEDL

## 📖 Documentation

- **🆕 Data Sources Guide**: [README_DATA_SOURCES.md](README_DATA_SOURCES.md) - Multi-source fetching
- **HDFC Analyzer**: [README_HDFC_ANALYZER.md](README_HDFC_ANALYZER.md)
- **Multi-Stock Analyzer**: [README_MULTI_STOCK.md](README_MULTI_STOCK.md)

## 🔧 Configuration

### Stock Selection
Edit `stocks_config.csv` to customize which stocks to analyze in the multi-stock analyzer.

### Data Source Configuration
Edit `data_source_config.json` to set preferred data sources:
```json
{
    "primary_source": "yahoo",
    "fallback_source": "google",
    "exchange": "NSE",
    "days": 30
}
```

## 📈 Output

Analysis results are generated as interactive HTML reports:
- `hdfc_bank_trends.html` - HDFC Bank analysis
- `multi_stock_trends.html` - Multi-stock portfolio analysis

## 🛠️ Requirements

- Python 3.7+
- pandas>=2.0.0
- yfinance>=0.2.40 (Yahoo Finance API)
- beautifulsoup4>=4.12.0 (Google Finance scraping)
- requests>=2.31.0
- ta>=0.11.0 (Technical analysis)
- Other dependencies listed in requirements files

## 📝 Notes

- All stock data is for the Indian stock market (NSE/BSE)
- Yahoo Finance symbols: `SYMBOL.NS` (NSE) or `SYMBOL.BO` (BSE)
- Google Finance format: `SYMBOL:NSE` or `SYMBOL:BSE`
- The system automatically handles symbol format conversion

## 🎯 Features

- ✅ Multi-source data fetching (Google + Yahoo)
- ✅ Automatic fallback mechanism
- ✅ Configurable data sources
- ✅ Technical indicators (RSI, MACD, CCI, etc.)
- ✅ Interactive HTML reports
- ✅ Real-time price monitoring
- ✅ Historical data analysis
- ✅ Multiple stock comparison

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r multi_stock_requirements.txt
   ```

2. **Run examples:**
   ```bash
   python example_data_sources.py
   ```

3. **Configure data sources:**
   Edit `data_source_config.json` to set preferences

4. **Analyze stocks:**
   ```bash
   python multi_stock_analyzer.py
   ```

For detailed usage and API documentation, see [README_DATA_SOURCES.md](README_DATA_SOURCES.md).