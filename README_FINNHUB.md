# Finnhub Integration Guide

## Overview

Finnhub is a professional-grade financial data API that provides real-time and historical stock market data. This integration adds Finnhub as a data source option for the stock analysis system.

## Features

- **Real-time Stock Quotes**: Get current market prices
- **Historical Data**: Access OHLCV (Open, High, Low, Close, Volume) data
- **Global Coverage**: Support for NSE, BSE, US exchanges, and more
- **Free Tier**: 60 API calls per minute on free plan
- **Professional Quality**: Reliable, accurate financial data

## Setup Instructions

### 1. Get Your API Key

1. Visit [Finnhub.io](https://finnhub.io/register)
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

### 2. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
export FINNHUB_API_KEY="your_api_key_here"
```

**Option B: .env File**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
FINNHUB_API_KEY=your_api_key_here
```

**Option C: Configuration File**
Edit `data_source_config.json`:
```json
{
    "primary_source": "yahoo",
    "fallback_source": "finnhub",
    "finnhub_api_key": "your_api_key_here"
}
```

### 3. Install Dependencies

No additional Python packages required! Finnhub integration uses the standard `requests` library.

## Usage

### Basic Usage

```python
from data_fetcher import DataFetcher

# Use Finnhub as primary source
fetcher = DataFetcher(
    primary_source='finnhub',
    fallback_source='yahoo',
    finnhub_api_key='your_api_key'  # Optional if using env var
)

# Fetch stock data
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)
print(data.head())
```

### Using Configuration Manager

```python
from data_fetcher import DataSourceConfig

# Load configuration
config = DataSourceConfig()

# Update to use Finnhub
config.update_config(
    primary_source='finnhub',
    fallback_source='yahoo',
    finnhub_api_key='your_api_key'
)

# Get configured fetcher
fetcher = config.get_fetcher()
data = fetcher.fetch_stock_data('RELIANCE', 'NSE', days=30)
```

### Multi-Source Strategy

```python
# Yahoo primary, Finnhub fallback (recommended)
fetcher = DataFetcher(
    primary_source='yahoo',
    fallback_source='finnhub'
)

# Finnhub primary, Yahoo fallback (requires API key)
fetcher = DataFetcher(
    primary_source='finnhub',
    fallback_source='yahoo'
)

# Three-way fallback
# If primary fails, tries fallback, then tries remaining source
```

## Symbol Format

### Indian Stocks (NSE)
- Input: `HDFCBANK`, Exchange: `NSE`
- Finnhub format: `HDFCBANK.NS`

### Indian Stocks (BSE)
- Input: `RELIANCE`, Exchange: `BSE`
- Finnhub format: `RELIANCE.BO`

### US Stocks
- Input: `AAPL`, Exchange: `US`
- Finnhub format: `AAPL`

The system automatically handles symbol conversion.

## API Limits

### Free Tier
- **Rate Limit**: 60 API calls per minute
- **Historical Data**: Available
- **Real-time Quotes**: Available
- **Cost**: Free forever

### Paid Tiers
- Higher rate limits
- Additional features
- See [Finnhub Pricing](https://finnhub.io/pricing)

## Data Quality Comparison

| Feature | Yahoo Finance | Google Finance | Finnhub |
|---------|--------------|----------------|---------|
| Historical Data | ✅ Excellent | ❌ Limited | ✅ Excellent |
| Real-time Quotes | ✅ Good | ✅ Good | ✅ Excellent |
| API Key Required | ❌ No | ❌ No | ✅ Yes |
| Rate Limits | ⚠️ Occasional | ⚠️ Varies | ✅ Clear limits |
| Reliability | ✅ High | ⚠️ Medium | ✅ Very High |
| Technical Indicators | ✅ Yes | ❌ No | ✅ Yes |
| Global Coverage | ✅ Good | ✅ Good | ✅ Excellent |

## Recommended Configurations

### For Development/Testing
```json
{
    "primary_source": "yahoo",
    "fallback_source": "finnhub"
}
```
- Uses free Yahoo Finance
- Falls back to Finnhub if needed
- Conserves API calls

### For Production
```json
{
    "primary_source": "finnhub",
    "fallback_source": "yahoo"
}
```
- Professional-grade data first
- Yahoo as reliable backup
- Best data quality

### For Maximum Reliability
```json
{
    "primary_source": "yahoo",
    "fallback_source": "finnhub"
}
```
- Two robust sources
- Automatic failover
- High availability

## Troubleshooting

### API Key Not Working
```
Error: ⚠️ Finnhub API key not configured
```
**Solution**: Set `FINNHUB_API_KEY` environment variable or pass to constructor

### Rate Limit Exceeded
```
Error: 429 Too Many Requests
```
**Solution**: 
- Wait 1 minute for rate limit reset
- Reduce API call frequency
- Consider upgrading plan

### Symbol Not Found
```
Error: No data available from Finnhub for SYMBOL.NS
```
**Solution**:
- Verify symbol is correct
- Check exchange code (NSE/BSE)
- Try alternative source

### No Data Returned
```
Error: Both sources failed for SYMBOL
```
**Solution**:
- Check internet connection
- Verify API key is valid
- Try different symbol
- Check Finnhub service status

## Examples

### Example 1: Single Stock Analysis
```python
from data_fetcher import DataFetcher
import os

# Set API key
os.environ['FINNHUB_API_KEY'] = 'your_key_here'

# Create fetcher
fetcher = DataFetcher(primary_source='finnhub')

# Fetch data
data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)

if data is not None:
    print(f"Fetched {len(data)} days of data")
    print(f"Latest close: ₹{data.iloc[-1]['Close']:.2f}")
```

### Example 2: Multiple Stocks
```python
stocks = [
    ('HDFCBANK', 'HDFC Bank'),
    ('RELIANCE', 'Reliance Industries'),
    ('INFY', 'Infosys')
]

fetcher = DataFetcher(primary_source='finnhub')
results = fetcher.fetch_multiple_stocks(stocks, exchange='NSE', days=30)

for symbol, info in results.items():
    print(f"{info['name']}: {len(info['data'])} days")
```

### Example 3: With Analyzers
```python
# The stock analyzers automatically use configured data source
# Just ensure FINNHUB_API_KEY is set

# Run HDFC analyzer
python3 hdfc_stock_analyzer.py

# Run multi-stock analyzer
python3 multi_stock_analyzer.py
```

## Best Practices

1. **Use Environment Variables**: Keep API keys secure
2. **Implement Caching**: Reduce API calls
3. **Handle Rate Limits**: Add delays between requests
4. **Use Fallbacks**: Configure multiple sources
5. **Monitor Usage**: Track API call consumption
6. **Validate Data**: Check for missing/invalid data
7. **Error Handling**: Gracefully handle API failures

## Security Notes

⚠️ **Important Security Practices**:

- Never commit API keys to version control
- Use `.env` files (add to `.gitignore`)
- Use environment variables in production
- Rotate keys periodically
- Monitor for unauthorized usage
- Use read-only keys when possible

## Support

- **Finnhub Documentation**: https://finnhub.io/docs/api
- **API Status**: https://status.finnhub.io/
- **Support**: support@finnhub.io
- **Community**: https://finnhub.io/community

## License

This integration is part of the Stock Analysis project. Finnhub API usage is subject to Finnhub's terms of service.

---

**Made with Bob** - Enhanced Stock Analysis System