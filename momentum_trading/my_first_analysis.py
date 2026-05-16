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