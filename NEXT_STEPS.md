# What to Do After Running the Test

After running `python test_momentum_system.py`, here's your step-by-step guide to start using the system.

---

## 🎯 Step 1: Create Your First Analysis Script

Create a new file called `my_first_analysis.py`:

```python
"""
My First Stock Analysis
Analyze a single stock with all indicators
"""

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators

# Configuration
STOCK_SYMBOL = 'HDFCBANK'  # Change this to any stock
DAYS = 90                   # Number of days to analyze

print("="*70)
print(f"ANALYZING {STOCK_SYMBOL}")
print("="*70)

# Step 1: Fetch Data
print("\n1. Fetching data...")
fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
data = fetcher.fetch_stock_data(STOCK_SYMBOL, exchange='NSE', days=DAYS)

if data is None or data.empty:
    print("❌ Could not fetch data. Try another stock or check internet.")
    exit()

print(f"✓ Fetched {len(data)} days of data")

# Step 2: Add Indicators
print("\n2. Calculating indicators...")
data = MomentumIndicators.add_all_momentum_indicators(data)
data = TrendIndicators.add_all_trend_indicators(data)
print(f"✓ Added {len(data.columns)} columns")

# Step 3: Analyze Latest Data
print("\n3. Latest Analysis:")
print("-"*70)

latest = data.iloc[-1]
prev = data.iloc[-2]

print(f"\n📅 Date: {latest['Date']}")
print(f"💰 Close Price: ₹{latest['Close']:.2f}")
print(f"📊 Volume: {latest['Volume']:,.0f}")

print(f"\n📈 MOMENTUM INDICATORS:")
print(f"   RSI (14): {latest['RSI']:.2f} {'🔴 Overbought' if latest['RSI'] > 70 else '🟢 Oversold' if latest['RSI'] < 30 else '🟡 Neutral'}")
print(f"   ROC (10): {latest['ROC']:.2f}%")
print(f"   MACD: {latest['MACD']:.2f} {'📈' if latest['MACD'] > latest['MACD_Signal'] else '📉'}")
print(f"   Stochastic K: {latest['Stoch_K']:.2f}")
print(f"   Momentum Score: {latest['Momentum_Score']:.2f}/100")

print(f"\n📊 TREND INDICATORS:")
print(f"   SuperTrend: ₹{latest['SuperTrend']:.2f}")
print(f"   Trend Direction: {'🟢 BULLISH' if latest['SuperTrend_Direction'] == 1 else '🔴 BEARISH'}")
print(f"   SMA(20): ₹{latest['SMA_20']:.2f}")
print(f"   SMA(50): ₹{latest['SMA_50']:.2f}")
print(f"   ADX: {latest['ADX']:.2f} ({latest['Trend_Strength']})")

# Step 4: Generate Signal
print(f"\n🎯 TRADING SIGNAL:")
print("-"*70)

# Calculate signal score
signal_score = 0
reasons = []

# Momentum checks
if latest['RSI'] > 50:
    signal_score += 20
    reasons.append("✓ RSI above 50 (bullish)")
else:
    signal_score -= 20
    reasons.append("✗ RSI below 50 (bearish)")

if latest['Momentum_Score'] > 60:
    signal_score += 20
    reasons.append("✓ Strong momentum")
elif latest['Momentum_Score'] < 40:
    signal_score -= 20
    reasons.append("✗ Weak momentum")

# Trend checks
if latest['SuperTrend_Direction'] == 1:
    signal_score += 30
    reasons.append("✓ SuperTrend bullish")
else:
    signal_score -= 30
    reasons.append("✗ SuperTrend bearish")

if latest['Close'] > latest['SMA_20']:
    signal_score += 15
    reasons.append("✓ Price above SMA(20)")
else:
    signal_score -= 15
    reasons.append("✗ Price below SMA(20)")

if latest['ADX'] > 25:
    signal_score += 15
    reasons.append("✓ Strong trend (ADX > 25)")

# Determine signal
if signal_score >= 60:
    signal = "🟢 STRONG BUY"
elif signal_score >= 30:
    signal = "🟢 BUY"
elif signal_score >= -30:
    signal = "🟡 HOLD"
elif signal_score >= -60:
    signal = "🔴 SELL"
else:
    signal = "🔴 STRONG SELL"

print(f"\nSignal: {signal}")
print(f"Score: {signal_score}/100")
print(f"\nReasons:")
for reason in reasons:
    print(f"  {reason}")

# Step 5: Show Recent Trend
print(f"\n📈 RECENT TREND (Last 5 Days):")
print("-"*70)
recent = data[['Date', 'Close', 'RSI', 'Momentum_Score', 'SuperTrend_Direction']].tail(5)
print(recent.to_string(index=False))

print("\n" + "="*70)
print("Analysis Complete!")
print("="*70)
```

**Run it:**
```bash
python my_first_analysis.py
```

---

## 🎯 Step 2: Analyze Multiple Stocks

Create `analyze_portfolio.py`:

```python
"""
Portfolio Analysis
Analyze multiple stocks and rank them
"""

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
import pandas as pd

# Your portfolio
STOCKS = [
    'HDFCBANK',
    'RELIANCE', 
    'INFY',
    'TCS',
    'ICICIBANK',
    'SBIN',
    'ITC',
    'LT'
]

print("="*80)
print("PORTFOLIO ANALYSIS")
print("="*80)

fetcher = DataFetcher(primary_source='yahoo')
results = []

for symbol in STOCKS:
    print(f"\nAnalyzing {symbol}...", end=" ")
    
    try:
        # Fetch data
        data = fetcher.fetch_stock_data(symbol, days=60)
        
        if data is None or data.empty:
            print("❌ No data")
            continue
        
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        data = TrendIndicators.add_all_trend_indicators(data)
        
        # Get latest
        latest = data.iloc[-1]
        
        # Calculate score
        score = 0
        if latest['RSI'] > 50: score += 20
        if latest['Momentum_Score'] > 60: score += 20
        if latest['SuperTrend_Direction'] == 1: score += 30
        if latest['Close'] > latest['SMA_20']: score += 15
        if latest['ADX'] > 25: score += 15
        
        # Determine signal
        if score >= 60:
            signal = "STRONG BUY"
        elif score >= 30:
            signal = "BUY"
        elif score >= -30:
            signal = "HOLD"
        else:
            signal = "SELL"
        
        results.append({
            'Symbol': symbol,
            'Close': latest['Close'],
            'RSI': latest['RSI'],
            'Momentum': latest['Momentum_Score'],
            'Trend': 'Bullish' if latest['SuperTrend_Direction'] == 1 else 'Bearish',
            'Score': score,
            'Signal': signal
        })
        
        print("✓")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Create results dataframe
df_results = pd.DataFrame(results)

# Sort by score
df_results = df_results.sort_values('Score', ascending=False)

print("\n" + "="*80)
print("RESULTS (Ranked by Score)")
print("="*80)
print(df_results.to_string(index=False))

print("\n" + "="*80)
print("TOP PICKS:")
print("="*80)

strong_buys = df_results[df_results['Signal'] == 'STRONG BUY']
if not strong_buys.empty:
    print("\n🟢 STRONG BUY:")
    for _, row in strong_buys.iterrows():
        print(f"   {row['Symbol']}: ₹{row['Close']:.2f} (Score: {row['Score']})")
else:
    print("\n🟢 No strong buy signals")

buys = df_results[df_results['Signal'] == 'BUY']
if not buys.empty:
    print("\n🟢 BUY:")
    for _, row in buys.iterrows():
        print(f"   {row['Symbol']}: ₹{row['Close']:.2f} (Score: {row['Score']})")

print("\n" + "="*80)
```

**Run it:**
```bash
python analyze_portfolio.py
```

---

## 🎯 Step 3: Use NSEpy for Open Interest Analysis

Create `oi_analysis.py`:

```python
"""
Open Interest Analysis
Analyze futures Open Interest for trading signals
"""

from momentum_trading.data.nse_fetcher import NSEDataFetcher

# Stocks to analyze
STOCKS = ['RELIANCE', 'HDFCBANK', 'INFY', 'TCS', 'ICICIBANK']

print("="*80)
print("OPEN INTEREST ANALYSIS")
print("="*80)

nse = NSEDataFetcher()

for symbol in STOCKS:
    print(f"\n{'='*80}")
    print(f"{symbol}")
    print('='*80)
    
    try:
        # Get OI analysis
        oi = nse.get_oi_analysis(symbol)
        
        if oi:
            print(f"\n📊 Signal: {oi['signal']}")
            print(f"📈 Type: {oi['interpretation']['type']}")
            print(f"📝 Description: {oi['interpretation']['description']}")
            print(f"\n💰 Latest OI: {oi['latest_oi']:,.0f}")
            print(f"📊 OI Change: {oi['oi_change']:,.0f} ({oi['oi_change_pct']:.2f}%)")
            print(f"💹 Price Change: {oi['price_change_pct']:.2f}%")
            
            # Trading recommendation
            if oi['signal'] == 'Bullish':
                print(f"\n🟢 RECOMMENDATION: Consider LONG positions")
            elif oi['signal'] == 'Bearish':
                print(f"\n🔴 RECOMMENDATION: Consider SHORT positions or exit longs")
            else:
                print(f"\n🟡 RECOMMENDATION: Wait for clearer signals")
        else:
            print("⚠️  No OI data available (market might be closed)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*80)
print("Analysis Complete!")
print("="*80)
print("\nNote: OI analysis works best during market hours")
```

**Run it:**
```bash
python oi_analysis.py
```

---

## 🎯 Step 4: Create a Daily Watchlist

Create `daily_watchlist.py`:

```python
"""
Daily Watchlist Generator
Creates a daily watchlist of stocks to watch
"""

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
from datetime import datetime

# Stocks to monitor
WATCHLIST = [
    'HDFCBANK', 'ICICIBANK', 'SBIN', 'AXISBANK',
    'RELIANCE', 'ONGC', 'IOC',
    'INFY', 'TCS', 'WIPRO', 'TECHM',
    'ITC', 'HINDUNILVR', 'ASIANPAINT',
    'LT', 'TATAMOTORS', 'TATASTEEL'
]

print("="*80)
print(f"DAILY WATCHLIST - {datetime.now().strftime('%Y-%m-%d')}")
print("="*80)

fetcher = DataFetcher(primary_source='yahoo')

buy_signals = []
sell_signals = []
watch_signals = []

for symbol in WATCHLIST:
    try:
        data = fetcher.fetch_stock_data(symbol, days=60)
        
        if data is None or data.empty:
            continue
        
        data = MomentumIndicators.add_all_momentum_indicators(data)
        data = TrendIndicators.add_all_trend_indicators(data)
        
        latest = data.iloc[-1]
        
        # Categorize
        if (latest['RSI'] > 60 and 
            latest['SuperTrend_Direction'] == 1 and 
            latest['Momentum_Score'] > 65):
            buy_signals.append({
                'Symbol': symbol,
                'Price': latest['Close'],
                'RSI': latest['RSI'],
                'Momentum': latest['Momentum_Score']
            })
        
        elif (latest['RSI'] < 40 and 
              latest['SuperTrend_Direction'] == -1 and 
              latest['Momentum_Score'] < 35):
            sell_signals.append({
                'Symbol': symbol,
                'Price': latest['Close'],
                'RSI': latest['RSI'],
                'Momentum': latest['Momentum_Score']
            })
        
        elif (45 < latest['RSI'] < 55 and 
              latest['Momentum_Score'] > 50):
            watch_signals.append({
                'Symbol': symbol,
                'Price': latest['Close'],
                'RSI': latest['RSI'],
                'Momentum': latest['Momentum_Score']
            })
        
        print(f"✓ {symbol}", end=" ")
        
    except:
        print(f"✗ {symbol}", end=" ")

print("\n\n" + "="*80)
print("🟢 BUY SIGNALS")
print("="*80)
if buy_signals:
    for stock in buy_signals:
        print(f"{stock['Symbol']:12} ₹{stock['Price']:8.2f}  RSI: {stock['RSI']:5.1f}  Momentum: {stock['Momentum']:5.1f}")
else:
    print("No buy signals today")

print("\n" + "="*80)
print("🔴 SELL SIGNALS")
print("="*80)
if sell_signals:
    for stock in sell_signals:
        print(f"{stock['Symbol']:12} ₹{stock['Price']:8.2f}  RSI: {stock['RSI']:5.1f}  Momentum: {stock['Momentum']:5.1f}")
else:
    print("No sell signals today")

print("\n" + "="*80)
print("🟡 WATCH LIST (Potential Breakouts)")
print("="*80)
if watch_signals:
    for stock in watch_signals:
        print(f"{stock['Symbol']:12} ₹{stock['Price']:8.2f}  RSI: {stock['RSI']:5.1f}  Momentum: {stock['Momentum']:5.1f}")
else:
    print("No stocks to watch")

print("\n" + "="*80)
print(f"Total Analyzed: {len(WATCHLIST)}")
print(f"Buy Signals: {len(buy_signals)}")
print(f"Sell Signals: {len(sell_signals)}")
print(f"Watch List: {len(watch_signals)}")
print("="*80)
```

**Run it:**
```bash
python daily_watchlist.py
```

---

## 📅 Daily Routine

### Morning (Before Market Opens)
```bash
python daily_watchlist.py
```
Review the watchlist and plan your trades.

### During Market Hours
```bash
python my_first_analysis.py  # Analyze specific stocks
python oi_analysis.py         # Check Open Interest
```

### After Market Close
```bash
python analyze_portfolio.py   # Review your portfolio
```

---

## 🎓 Learning Path

### Week 1: Learn the Basics
- Run all example scripts
- Understand each indicator
- Read ARCHITECTURE.md

### Week 2: Customize
- Modify the scoring logic
- Add your own indicators
- Create custom strategies

### Week 3: Backtest
- Test strategies on historical data
- Calculate win rates
- Optimize parameters

### Week 4: Paper Trade
- Test with fake money
- Track performance
- Refine strategy

---

## 📚 Next Documentation to Read

1. **ARCHITECTURE.md** - Understand the system design
2. **momentum_trading/README.md** - Detailed API docs
3. **QUICK_START_GUIDE.md** - More examples

---

## ✅ Your Action Plan

- [ ] Run `my_first_analysis.py` with different stocks
- [ ] Run `analyze_portfolio.py` with your stocks
- [ ] Run `oi_analysis.py` during market hours
- [ ] Set up `daily_watchlist.py` for daily use
- [ ] Customize the scoring logic
- [ ] Build your own strategy
- [ ] Start paper trading

---

**You're ready to start trading! 🚀**

Remember: Always paper trade first before using real money!