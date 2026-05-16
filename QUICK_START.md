# Quick Start Guide - Stock Analysis with Multi-Source Data

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd StockAnalysis
pip install -r multi_stock_requirements.txt
```

### Step 2: Test Data Sources
```bash
python example_data_sources.py
```

### Step 3: Configure Your Preferences
Edit `data_source_config.json`:
```json
{
    "primary_source": "yahoo",
    "fallback_source": "google",
    "exchange": "NSE",
    "days": 30
}
```

## 📊 Common Use Cases

### Get Current Stock Price
```python
from data_fetcher import DataFetcher

fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
price = fetcher.get_current_price('HDFCBANK', 'NSE')
print(f"HDFC Bank: ₹{price}")
```

### Fetch Historical Data
```python
from data_fetcher import DataFetcher

fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
data = fetcher.fetch_stock_data('RELIANCE', 'NSE', days=30)
print(data.tail())
```

### Analyze Multiple Stocks
```python
from data_fetcher import DataFetcher

stocks = [
    ('HDFCBANK', 'HDFC Bank'),
    ('RELIANCE', 'Reliance Industries'),
    ('TCS', 'Tata Consultancy Services')
]

fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
results = fetcher.fetch_multiple_stocks(stocks, exchange='NSE', days=30)

for symbol, info in results.items():
    print(f"{info['name']}: {len(info['data'])} days")
```

### Use Configuration Manager
```python
from data_fetcher import DataSourceConfig

config = DataSourceConfig()
config.update_config(primary_source='google', days=60)

fetcher = config.get_fetcher()
data = fetcher.fetch_stock_data('INFY', 'NSE')
```

## 🎯 Data Source Selection Guide

| Use Case | Recommended Primary | Fallback |
|----------|-------------------|----------|
| Real-time prices | Google Finance | Yahoo Finance |
| Historical analysis | Yahoo Finance | Google Finance |
| Technical indicators | Yahoo Finance | Yahoo Finance |
| Quick price check | Google Finance | Yahoo Finance |
| Backtesting | Yahoo Finance | None |

## 🔧 Troubleshooting

### Issue: "No data found"
**Solution**: Check internet connection and symbol format
- NSE: `HDFCBANK` (not HDFCBANK.NS)
- BSE: Use exchange='BSE'

### Issue: "Import error"
**Solution**: Install dependencies
```bash
pip install -r multi_stock_requirements.txt
```

### Issue: "Rate limit exceeded"
**Solution**: Add delays between requests
```python
import time
time.sleep(1)  # Wait 1 second between requests
```

## 📚 Next Steps

1. **Read Full Documentation**: [README_DATA_SOURCES.md](README_DATA_SOURCES.md)
2. **Run Examples**: `python example_data_sources.py`
3. **Customize Configuration**: Edit `data_source_config.json`
4. **Integrate with Analyzers**: See integration examples in documentation

## 💡 Pro Tips

1. **Use Yahoo for historical data** - More reliable and complete
2. **Use Google for current prices** - Faster for real-time checks
3. **Enable fallback** - Always set a fallback source
4. **Cache results** - Avoid repeated API calls
5. **Respect rate limits** - Add delays between bulk requests

## 🆘 Need Help?

- Check [README_DATA_SOURCES.md](README_DATA_SOURCES.md) for detailed documentation
- Run `python example_data_sources.py` to see working examples
- Review `data_fetcher.py` for API reference

## ⚡ One-Liner Examples

```python
# Quick price check
from data_fetcher import DataFetcher; print(DataFetcher().get_current_price('HDFCBANK', 'NSE'))

# Fetch 30 days of data
from data_fetcher import DataFetcher; data = DataFetcher().fetch_stock_data('RELIANCE', 'NSE', 30)

# Use configuration
from data_fetcher import DataSourceConfig; fetcher = DataSourceConfig().get_fetcher()
```

Happy Analyzing! 📈