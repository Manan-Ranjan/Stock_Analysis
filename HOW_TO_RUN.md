# How to Run - Simple Steps

## 🚀 Quick Start (3 Steps)

### Step 1: Open Terminal in VS Code

In VS Code:
1. Click **Terminal** menu → **New Terminal**
2. Or press `` Ctrl+` `` (backtick key)

You should see a terminal at the bottom of VS Code showing:
```
/Users/manishranjan/MyProjects/LangChain/StockAnalysis
```

### Step 2: Install Required Packages

Copy and paste this command in the terminal:

```bash
pip install pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib
```

Press **Enter** and wait for installation to complete (1-2 minutes).

### Step 3: Run the Test

Copy and paste this command:

```bash
python test_momentum_system.py
```

Press **Enter**. You should see test results!

---

## 📋 Detailed Instructions

### Option A: Run the Complete Test

```bash
# In VS Code terminal, run:
python test_momentum_system.py
```

This tests everything automatically.

### Option B: Run Individual Examples

#### Example 1: Test NSEpy Data Fetcher

Create a new file `test_nsepy.py`:

```python
from momentum_trading.data.nse_fetcher import NSEDataFetcher

# Initialize
nse = NSEDataFetcher()

# Fetch HDFC Bank data
print("Fetching HDFCBANK data...")
data = nse.fetch_stock_data('HDFCBANK', days=5)

if data is not None:
    print("\n✓ Success! Here's the data:")
    print(data[['Date', 'Close', 'Volume']].tail())
else:
    print("⚠️  No data (market might be closed)")
```

Run it:
```bash
python test_nsepy.py
```

#### Example 2: Test Indicators

Create a new file `test_indicators.py`:

```python
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators

# Fetch data
print("Fetching INFY data...")
fetcher = DataFetcher(primary_source='yahoo')
data = fetcher.fetch_stock_data('INFY', exchange='NSE', days=60)

if data is not None:
    print("✓ Data fetched!")
    
    # Add indicators
    print("Calculating indicators...")
    data = MomentumIndicators.add_all_momentum_indicators(data)
    data = TrendIndicators.add_all_trend_indicators(data)
    
    # Show results
    latest = data.iloc[-1]
    print(f"\n📊 Analysis for INFY:")
    print(f"Close Price: ₹{latest['Close']:.2f}")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"Momentum Score: {latest['Momentum_Score']:.2f}")
    print(f"SuperTrend: ₹{latest['SuperTrend']:.2f}")
    print(f"Trend: {'📈 Bullish' if latest['SuperTrend_Direction']==1 else '📉 Bearish'}")
    
    # Simple signal
    if latest['RSI'] > 60 and latest['Momentum_Score'] > 60:
        print("\n🟢 Signal: BUY")
    elif latest['RSI'] < 40 and latest['Momentum_Score'] < 40:
        print("\n🔴 Signal: SELL")
    else:
        print("\n🟡 Signal: HOLD")
```

Run it:
```bash
python test_indicators.py
```

#### Example 3: Analyze Multiple Stocks

Create a new file `analyze_stocks.py`:

```python
from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators

# List of stocks to analyze
stocks = ['HDFCBANK', 'RELIANCE', 'INFY', 'TCS']

fetcher = DataFetcher(primary_source='yahoo')

print("="*60)
print("STOCK ANALYSIS")
print("="*60)

for symbol in stocks:
    print(f"\n{symbol}:")
    
    # Fetch data
    data = fetcher.fetch_stock_data(symbol, days=30)
    
    if data is not None:
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        
        # Get latest
        latest = data.iloc[-1]
        
        print(f"  Close: ₹{latest['Close']:.2f}")
        print(f"  RSI: {latest['RSI']:.2f}")
        print(f"  Momentum: {latest['Momentum_Score']:.2f}")
        
        # Signal
        if latest['Momentum_Score'] > 60:
            print(f"  Signal: 🟢 BULLISH")
        elif latest['Momentum_Score'] < 40:
            print(f"  Signal: 🔴 BEARISH")
        else:
            print(f"  Signal: 🟡 NEUTRAL")
    else:
        print(f"  ⚠️  Could not fetch data")

print("\n" + "="*60)
```

Run it:
```bash
python analyze_stocks.py
```

---

## 🎯 What Each Command Does

### Install Command
```bash
pip install pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib
```
- Installs all required Python packages
- Takes 1-2 minutes
- Only needs to be done once

### Test Command
```bash
python test_momentum_system.py
```
- Runs comprehensive tests
- Checks if everything works
- Shows example outputs

### Individual Module Tests
```bash
python -m momentum_trading.data.nse_fetcher
```
- Tests just the NSEpy data fetcher
- Shows example data

```bash
python -m momentum_trading.indicators.momentum
```
- Tests momentum indicators
- Shows RSI, ROC, MACD, etc.

```bash
python -m momentum_trading.indicators.trend
```
- Tests trend indicators
- Shows SuperTrend, MA, ADX, etc.

---

## 🖥️ Using Python Interactive Mode

You can also run commands interactively:

```bash
# Start Python
python

# Then type commands one by one:
>>> from momentum_trading.data.nse_fetcher import NSEDataFetcher
>>> nse = NSEDataFetcher()
>>> data = nse.fetch_stock_data('HDFCBANK', days=5)
>>> print(data.head())

# Exit Python
>>> exit()
```

---

## 📝 Using Jupyter Notebook (Optional)

If you have Jupyter installed:

```bash
# Install Jupyter
pip install jupyter

# Start Jupyter
jupyter notebook

# Create new notebook and run code cells
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "pip: command not found"
**Solution:**
```bash
# Try pip3 instead
pip3 install pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib
```

### Issue 2: "No module named 'momentum_trading'"
**Solution:**
```bash
# Make sure you're in the correct directory
cd /Users/manishranjan/MyProjects/LangChain/StockAnalysis

# Then run the command again
python test_momentum_system.py
```

### Issue 3: "Permission denied"
**Solution:**
```bash
# Add --user flag
pip install --user pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib
```

### Issue 4: NSEpy returns no data
**Reason:** NSE market might be closed or network issue
**Solution:** Try Yahoo Finance instead:
```python
fetcher = DataFetcher(primary_source='yahoo')
```

---

## 🎓 Learning Path

### Beginner
1. Run `python test_momentum_system.py`
2. Try Example 1 (NSEpy)
3. Try Example 2 (Indicators)

### Intermediate
1. Try Example 3 (Multiple stocks)
2. Modify the examples
3. Create your own analysis

### Advanced
1. Read ARCHITECTURE.md
2. Build custom strategies
3. Add backtesting

---

## 📞 Need Help?

If something doesn't work:

1. **Check you're in the right directory:**
   ```bash
   pwd
   # Should show: /Users/manishranjan/MyProjects/LangChain/StockAnalysis
   ```

2. **Check Python version:**
   ```bash
   python --version
   # Should be Python 3.8 or higher
   ```

3. **Reinstall packages:**
   ```bash
   pip install --upgrade pandas numpy yfinance nsepy requests beautifulsoup4 ta
   ```

4. **Check the error message** - It usually tells you what's wrong!

---

## ✅ Quick Checklist

- [ ] Open VS Code terminal
- [ ] Run: `pip install pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib`
- [ ] Wait for installation
- [ ] Run: `python test_momentum_system.py`
- [ ] See test results
- [ ] Try examples above
- [ ] Start building your strategy!

---

## 🚀 Ready to Start?

**Just run these 2 commands:**

```bash
# 1. Install packages
pip install pandas numpy yfinance nsepy requests beautifulsoup4 ta plotly matplotlib

# 2. Run test
python test_momentum_system.py
```

**That's it!** 🎉

The test will show you if everything works and give you example outputs.