# Stock Data Sources Guide

## 📊 Overview

The stock analysis system now supports **multiple data sources** with automatic fallback mechanism:

1. **Google Finance** (Web Scraping)
2. **Yahoo Finance** (API)

## 🚀 Quick Start

### Using the Data Fetcher

```python
from data_fetcher import DataFetcher

# Option 1: Google Finance primary, Yahoo fallback
fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)

# Option 2: Yahoo Finance primary, Google fallback
fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
data = fetcher.fetch_stock_data('RELIANCE', 'NSE', days=30)

# Option 3: Get current price quickly
price = fetcher.get_current_price('INFY', 'NSE')
print(f"Current price: ₹{price}")
```

### Using Configuration Manager

```python
from data_fetcher import DataSourceConfig

# Load configuration
config = DataSourceConfig()

# Update configuration
config.update_config(
    primary_source='google',
    fallback_source='yahoo',
    days=60
)

# Get configured fetcher
fetcher = config.get_fetcher()
data = fetcher.fetch_stock_data('TCS', 'NSE')
```

## 📁 Configuration File

Edit `data_source_config.json` to customize behavior:

```json
{
    "primary_source": "yahoo",
    "fallback_source": "google",
    "exchange": "NSE",
    "days": 30,
    "use_cache": true,
    "cache_duration_hours": 1
}
```

### Configuration Options

| Parameter | Options | Description |
|-----------|---------|-------------|
| `primary_source` | `google`, `yahoo` | First data source to try |
| `fallback_source` | `google`, `yahoo` | Backup if primary fails |
| `exchange` | `NSE`, `BSE` | Indian stock exchange |
| `days` | Integer | Days of historical data |
| `use_cache` | `true`, `false` | Enable data caching |
| `cache_duration_hours` | Integer | Cache validity period |

## 🔍 Data Source Comparison

### Google Finance

**Method**: Web Scraping

**Pros**:
- ✅ Real-time current prices
- ✅ No API key required
- ✅ Direct from Google's interface
- ✅ Good for quick price checks

**Cons**:
- ❌ Limited historical data access
- ❌ May break if Google changes UI
- ❌ Slower than API calls
- ❌ No technical indicators

**Best For**: Current price lookups, real-time monitoring

**URL Format**: `https://www.google.com/finance/quote/SYMBOL:EXCHANGE`

### Yahoo Finance

**Method**: Official API (via yfinance library)

**Pros**:
- ✅ Extensive historical data (years)
- ✅ Reliable and stable API
- ✅ Rich technical indicators
- ✅ Volume and OHLC data
- ✅ Actively maintained library

**Cons**:
- ❌ Occasional rate limits
- ❌ May have slight delays

**Best For**: Historical analysis, technical indicators, backtesting

**Symbol Format**: `SYMBOL.NS` (NSE) or `SYMBOL.BO` (BSE)

## 🔄 Hybrid Approach

The system automatically tries the primary source first, then falls back to the secondary source if:
- Network error occurs
- Data not found
- Parsing fails
- Timeout occurs

```python
# This will try Google first, then Yahoo if Google fails
fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE')
```

## 📦 Installation

Install required dependencies:

```bash
pip install -r multi_stock_requirements.txt
```

Required packages:
- `yfinance>=0.2.40` - Yahoo Finance API
- `beautifulsoup4>=4.12.0` - HTML parsing for Google Finance
- `requests>=2.31.0` - HTTP requests
- `pandas>=2.0.0` - Data manipulation
- `ta>=0.11.0` - Technical analysis indicators

## 🎯 Use Cases

### Use Case 1: Real-time Price Monitoring
**Recommended**: Google Finance primary
```python
fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
price = fetcher.get_current_price('RELIANCE', 'NSE')
```

### Use Case 2: Historical Analysis
**Recommended**: Yahoo Finance primary
```python
fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=90)
```

### Use Case 3: Technical Analysis
**Recommended**: Yahoo Finance only
```python
fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
data = fetcher.fetch_stock_data('INFY', 'NSE', days=30)
# Data includes OHLCV for indicator calculation
```

### Use Case 4: Multiple Stocks
```python
stocks = [
    ('HDFCBANK', 'HDFC Bank'),
    ('RELIANCE', 'Reliance Industries'),
    ('TCS', 'Tata Consultancy Services')
]

fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
results = fetcher.fetch_multiple_stocks(stocks, exchange='NSE', days=30)

for symbol, info in results.items():
    print(f"{info['name']}: {len(info['data'])} days of data")
```

## 🛠️ Integration with Existing Analyzers

### Updating multi_stock_analyzer.py

Replace the `fetch_stock_data` method:

```python
from data_fetcher import DataSourceConfig

class MultiStockAnalyzer:
    def __init__(self):
        # ... existing code ...
        self.config = DataSourceConfig()
        self.fetcher = self.config.get_fetcher()
    
    def fetch_stock_data(self, symbol, name):
        """Fetch using configured data source"""
        data = self.fetcher.fetch_stock_data(symbol, 'NSE', days=30)
        
        if data is None:
            return self._generate_sample_data(symbol, name)
        
        # Continue with technical indicator calculation...
        return data
```

## 🔧 Troubleshooting

### Google Finance Issues

**Problem**: "Could not find price element"
- **Solution**: Google may have changed their HTML structure. Check the class names in the scraper.

**Problem**: "Request timeout"
- **Solution**: Increase timeout or check internet connection.

### Yahoo Finance Issues

**Problem**: "No data found for symbol"
- **Solution**: Verify symbol format (should be SYMBOL.NS for NSE)

**Problem**: "Rate limit exceeded"
- **Solution**: Add delays between requests or reduce frequency.

## 📊 Data Format

Both sources return data in consistent format:

```python
{
    'Date': ['2024-01-01', '2024-01-02', ...],
    'Symbol': ['HDFCBANK', 'HDFCBANK', ...],
    'Close': [1500.50, 1505.25, ...],
    'Open': [1498.00, 1501.00, ...],
    'High': [1510.00, 1508.00, ...],
    'Low': [1495.00, 1500.00, ...],
    'Volume': [1000000, 1200000, ...],
    'Source': ['Yahoo Finance', 'Yahoo Finance', ...]
}
```

## 🚨 Important Notes

1. **Google Finance Limitation**: Web scraping provides current data only. For historical data, Yahoo Finance is automatically used.

2. **Rate Limits**: Be respectful of API limits. Add delays between requests when fetching multiple stocks.

3. **Data Accuracy**: Always verify critical trading decisions with official sources.

4. **Legal Compliance**: Ensure your use complies with terms of service of both Google and Yahoo Finance.

## 📚 Examples

See `data_fetcher.py` for complete examples at the bottom of the file.

Run examples:
```bash
cd StockAnalysis
python data_fetcher.py
```

## 🔗 Resources

- [Yahoo Finance API Documentation](https://github.com/ranaroussi/yfinance)
- [Google Finance](https://www.google.com/finance/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Technical Analysis Library](https://technical-analysis-library-in-python.readthedocs.io/)

## 📝 License

This tool is for educational and personal use. Respect the terms of service of data providers.