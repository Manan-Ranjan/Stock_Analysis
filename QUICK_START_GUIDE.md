# Quick Start Guide - Momentum Trading System

## 🚀 Installation & Testing

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd /Users/manishranjan/MyProjects/LangChain/StockAnalysis

# Install all required packages
pip install -r momentum_trading/requirements.txt
```

**Key Dependencies:**
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `yfinance` - Yahoo Finance data
- `nsepy` - NSE India data with Open Interest
- `ta` - Technical analysis indicators
- `requests` - HTTP requests
- `beautifulsoup4` - Web scraping

### Step 2: Run the Test Script

```bash
# Run comprehensive test
python test_momentum_system.py
```

This will test:
1. ✅ All dependencies
2. ✅ NSEpy data fetcher
3. ✅ Unified data fetcher
4. ✅ Momentum indicators
5. ✅ Trend indicators
6. ✅ Complete workflow

### Step 3: Quick Examples

#### Example 1: Fetch Stock Data with NSEpy

```python
from momentum_trading.data.nse_fetcher import NSEDataFetcher

# Initialize NSE fetcher
nse = NSEDataFetcher()

# Fetch stock data
data = nse.fetch_stock_data('HDFCBANK', days=30)
print(data.head())

# Fetch futures with Open Interest
futures = nse.fetch_futures_data('RELIANCE', days=30)
print(futures[['Date', 'Close', 'OI', 'OI_Change']].tail())

# Get OI analysis
oi_analysis = nse.get_oi_analysis('RELIANCE')
print(f"Signal: {oi_analysis['signal']}")
print(f"Type: {oi_analysis['interpretation']['type']}")
```

#### Example 2: Calculate Technical Indicators

```python
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators

# Fetch data
fetcher = DataFetcher(primary_source='yahoo')
data = fetcher.fetch_stock_data('INFY', exchange='NSE', days=90)

# Add momentum indicators
data = MomentumIndicators.add_all_momentum_indicators(data)

# Add trend indicators
data = TrendIndicators.add_all_trend_indicators(data)

# View results
print(data[['Date', 'Close', 'RSI', 'SuperTrend', 'Momentum_Score']].tail())
```

#### Example 3: Analyze Multiple Stocks

```python
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators

# Fetch multiple stocks
fetcher = DataFetcher(primary_source='yahoo')
stocks = ['HDFCBANK', 'RELIANCE', 'INFY', 'TCS']

for symbol in stocks:
    print(f"\n{'='*60}")
    print(f"Analyzing {symbol}")
    print('='*60)
    
    # Fetch data
    data = fetcher.fetch_stock_data(symbol, days=30)
    
    if data is not None:
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        
        # Get latest values
        latest = data.iloc[-1]
        print(f"Close: ₹{latest['Close']:.2f}")
        print(f"RSI: {latest['RSI']:.2f}")
        print(f"Momentum Score: {latest['Momentum_Score']:.2f}")
        
        # Simple signal
        if latest['RSI'] > 60 and latest['Momentum_Score'] > 60:
            print("📈 Signal: BULLISH")
        elif latest['RSI'] < 40 and latest['Momentum_Score'] < 40:
            print("📉 Signal: BEARISH")
        else:
            print("➡️  Signal: NEUTRAL")
```

## 🧪 Testing Individual Modules

### Test NSEpy Fetcher

```bash
python -m momentum_trading.data.nse_fetcher
```

### Test Momentum Indicators

```bash
python -m momentum_trading.indicators.momentum
```

### Test Trend Indicators

```bash
python -m momentum_trading.indicators.trend
```

### Test Unified Fetcher

```bash
python -m momentum_trading.data.fetcher
```

## 📊 Understanding the Output

### RSI (Relative Strength Index)
- **> 70**: Overbought (potential sell signal)
- **50-70**: Bullish momentum
- **30-50**: Bearish momentum
- **< 30**: Oversold (potential buy signal)

### SuperTrend
- **Direction = 1**: Uptrend (bullish)
- **Direction = -1**: Downtrend (bearish)
- **Price > SuperTrend**: Buy signal
- **Price < SuperTrend**: Sell signal

### Momentum Score (0-100)
- **80-100**: Strong Buy
- **60-80**: Buy
- **40-60**: Hold/Neutral
- **20-40**: Sell
- **0-20**: Strong Sell

### Open Interest Analysis
- **Long Build-up**: Price ↑ + OI ↑ (Bullish)
- **Short Build-up**: Price ↓ + OI ↑ (Bearish)
- **Short Covering**: Price ↑ + OI ↓ (Bullish)
- **Long Unwinding**: Price ↓ + OI ↓ (Bearish)

## 🔧 Troubleshooting

### Issue: NSEpy not working

**Solution:**
```bash
pip install --upgrade nsepy
```

NSEpy requires:
- Active internet connection
- May need market hours for some data
- Some data might be delayed

### Issue: Yahoo Finance rate limit

**Solution:**
```python
# Add delay between requests
import time
time.sleep(1)  # Wait 1 second between requests
```

### Issue: Missing dependencies

**Solution:**
```bash
# Install specific package
pip install package_name

# Or reinstall all
pip install -r momentum_trading/requirements.txt --upgrade
```

### Issue: Import errors

**Solution:**
```python
# Make sure you're in the correct directory
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
```

## 📁 Project Structure

```
StockAnalysis/
├── ARCHITECTURE.md                    # System architecture
├── QUICK_START_GUIDE.md              # This file
├── test_momentum_system.py           # Comprehensive test script
│
├── momentum_trading/                  # Main package
│   ├── __init__.py
│   ├── README.md                     # Detailed documentation
│   ├── requirements.txt              # Dependencies
│   │
│   ├── data/                         # Data fetching
│   │   ├── __init__.py
│   │   ├── nse_fetcher.py           # NSEpy integration
│   │   └── fetcher.py               # Unified fetcher
│   │
│   └── indicators/                   # Technical indicators
│       ├── __init__.py
│       ├── momentum.py              # Momentum indicators
│       └── trend.py                 # Trend indicators
│
└── [existing files...]
```

## 🎯 Next Steps

### 1. Run the Test
```bash
python test_momentum_system.py
```

### 2. Try Examples
Copy and run the examples above in a Python script or Jupyter notebook.

### 3. Explore the Code
- Read `ARCHITECTURE.md` for system design
- Read `momentum_trading/README.md` for detailed API docs
- Check individual module files for more examples

### 4. Build Your Strategy
```python
# Your custom strategy
def my_strategy(data):
    latest = data.iloc[-1]
    
    # Define your rules
    if (latest['RSI'] > 60 and 
        latest['SuperTrend_Direction'] == 1 and 
        latest['Momentum_Score'] > 70):
        return "STRONG BUY"
    
    elif (latest['RSI'] < 40 and 
          latest['SuperTrend_Direction'] == -1 and 
          latest['Momentum_Score'] < 30):
        return "STRONG SELL"
    
    else:
        return "HOLD"

# Use it
signal = my_strategy(data)
print(f"Signal: {signal}")
```

## 📚 Additional Resources

- **NSEpy Documentation**: https://nsepy.xyz/
- **TA Library**: https://technical-analysis-library-in-python.readthedocs.io/
- **Yahoo Finance**: https://pypi.org/project/yfinance/
- **Pandas**: https://pandas.pydata.org/docs/

## 💡 Tips

1. **Start Simple**: Begin with one stock and basic indicators
2. **Test Thoroughly**: Use historical data to validate your strategy
3. **Paper Trade**: Test with paper trading before real money
4. **Risk Management**: Always use stop losses
5. **Stay Updated**: Markets change, adapt your strategy

## 🆘 Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify all dependencies are installed
3. Check if you're using the correct data source
4. Review the examples in the code
5. Check if NSE is open (for NSEpy data)

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Test script runs successfully
- [ ] Can fetch stock data
- [ ] Can calculate indicators
- [ ] Understand the signals
- [ ] Ready to build strategy

---

**Happy Trading! 📈**

Remember: This is for educational purposes. Always do your own research and never invest more than you can afford to lose.