"""
Portfolio Analysis
Analyze multiple stocks and rank them by momentum score
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
import pandas as pd
import time

# Your portfolio - Edit this list
STOCKS = [
    'HDFCBANK',
    'RELIANCE', 
    'INFY',
    'TCS',
    'ICICIBANK',
    'SBIN',
    'ITC',
    'LT',
    'TATAMOTORS',
    'WIPRO',
    'VEDANTA',
    'PFC',
    'ICICI Bank',
    'IRCTC',
    'SAIL',
    'TCS',
    'IOC',
    'ADANI POWER',
    'HINDUNILVR',
    'ASIAN PAINTS',
    'ADANI ENTERPRISES',
    'HAL',
    'TATA STEEL',
    'JIO FINANCIAL SERVICES',
    'OIL INDIA'
    ]

print("="*80)
print("PORTFOLIO ANALYSIS")
print("="*80)
print(f"Analyzing {len(STOCKS)} stocks...")

fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
results = []

for i, symbol in enumerate(STOCKS, 1):
    print(f"\n[{i}/{len(STOCKS)}] Analyzing {symbol}...", end=" ")
    
    try:
        # Fetch data
        data = fetcher.fetch_stock_data(symbol, exchange='NSE', days=60)
        
        if data is None or data.empty:
            print("❌ No data")
            continue
        
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        data = TrendIndicators.add_all_trend_indicators(data)
        
        # Get latest
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # Calculate score
        score = 0
        
        # Momentum checks (40 points)
        if latest['RSI'] > 50:
            score += 20
        if latest['Momentum_Score'] > 60:
            score += 20
        elif latest['Momentum_Score'] < 40:
            score -= 20
        
        # Trend checks (40 points)
        if latest['SuperTrend_Direction'] == 1:
            score += 30
        else:
            score -= 30
        
        if latest['Close'] > latest['SMA_20']:
            score += 10
        else:
            score -= 10
        
        # Strength checks (20 points)
        if latest['ADX'] > 25:
            score += 20
        
        # Determine signal
        if score >= 60:
            signal = "STRONG BUY"
            emoji = "🟢"
        elif score >= 30:
            signal = "BUY"
            emoji = "🟢"
        elif score >= -30:
            signal = "HOLD"
            emoji = "🟡"
        elif score >= -60:
            signal = "SELL"
            emoji = "🔴"
        else:
            signal = "STRONG SELL"
            emoji = "🔴"
        
        # Calculate price change
        price_change = ((latest['Close'] - prev['Close']) / prev['Close'] * 100) if len(data) > 1 else 0
        
        results.append({
            'Symbol': symbol,
            'Close': latest['Close'],
            'Change%': price_change,
            'RSI': latest['RSI'],
            'Momentum': latest['Momentum_Score'],
            'Trend': 'Bullish' if latest['SuperTrend_Direction'] == 1 else 'Bearish',
            'ADX': latest['ADX'],
            'Score': score,
            'Signal': signal,
            'Emoji': emoji
        })
        
        print(f"✓ Score: {score}")
        
        # Be nice to servers
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")

# Create results dataframe
if not results:
    print("\n❌ No data fetched. Check your internet connection.")
    exit()

df_results = pd.DataFrame(results)

# Sort by score
df_results = df_results.sort_values('Score', ascending=False)

print("\n" + "="*80)
print("RESULTS (Ranked by Score)")
print("="*80)
print()

# Format and display
for _, row in df_results.iterrows():
    print(f"{row['Emoji']} {row['Symbol']:12} ₹{row['Close']:8.2f} ({row['Change%']:+6.2f}%)  "
          f"RSI:{row['RSI']:5.1f}  Mom:{row['Momentum']:5.1f}  "
          f"ADX:{row['ADX']:5.1f}  Score:{row['Score']:4}  {row['Signal']}")

print("\n" + "="*80)
print("SUMMARY BY SIGNAL")
print("="*80)

# Count signals
signal_counts = df_results['Signal'].value_counts()

strong_buys = df_results[df_results['Signal'] == 'STRONG BUY']
buys = df_results[df_results['Signal'] == 'BUY']
holds = df_results[df_results['Signal'] == 'HOLD']
sells = df_results[df_results['Signal'] == 'SELL']
strong_sells = df_results[df_results['Signal'] == 'STRONG SELL']

if not strong_buys.empty:
    print("\n🟢 STRONG BUY:")
    for _, row in strong_buys.iterrows():
        print(f"   {row['Symbol']:12} ₹{row['Close']:8.2f}  Score: {row['Score']:3}  "
              f"RSI: {row['RSI']:.1f}  Momentum: {row['Momentum']:.1f}")

if not buys.empty:
    print("\n🟢 BUY:")
    for _, row in buys.iterrows():
        print(f"   {row['Symbol']:12} ₹{row['Close']:8.2f}  Score: {row['Score']:3}  "
              f"RSI: {row['RSI']:.1f}  Momentum: {row['Momentum']:.1f}")

if not holds.empty:
    print("\n🟡 HOLD:")
    for _, row in holds.iterrows():
        print(f"   {row['Symbol']:12} ₹{row['Close']:8.2f}  Score: {row['Score']:3}")

if not sells.empty:
    print("\n🔴 SELL:")
    for _, row in sells.iterrows():
        print(f"   {row['Symbol']:12} ₹{row['Close']:8.2f}  Score: {row['Score']:3}")

if not strong_sells.empty:
    print("\n🔴 STRONG SELL:")
    for _, row in strong_sells.iterrows():
        print(f"   {row['Symbol']:12} ₹{row['Close']:8.2f}  Score: {row['Score']:3}")

print("\n" + "="*80)
print("STATISTICS")
print("="*80)
print(f"Total Stocks Analyzed: {len(df_results)}")
print(f"Strong Buy: {len(strong_buys)}")
print(f"Buy: {len(buys)}")
print(f"Hold: {len(holds)}")
print(f"Sell: {len(sells)}")
print(f"Strong Sell: {len(strong_sells)}")

print(f"\nAverage Score: {df_results['Score'].mean():.1f}")
print(f"Average RSI: {df_results['RSI'].mean():.1f}")
print(f"Average Momentum: {df_results['Momentum'].mean():.1f}")

# Top 3 picks
print("\n" + "="*80)
print("🏆 TOP 3 PICKS")
print("="*80)
top3 = df_results.head(3)
for i, (_, row) in enumerate(top3.iterrows(), 1):
    print(f"\n{i}. {row['Symbol']}")
    print(f"   Price: ₹{row['Close']:.2f} ({row['Change%']:+.2f}%)")
    print(f"   Signal: {row['Emoji']} {row['Signal']}")
    print(f"   Score: {row['Score']}")
    print(f"   RSI: {row['RSI']:.1f} | Momentum: {row['Momentum']:.1f} | Trend: {row['Trend']}")

print("\n" + "="*80)
print("Analysis Complete!")
print("="*80)
print("\nTip: Edit the STOCKS list at the top to analyze your own portfolio!")

# Made with Bob
