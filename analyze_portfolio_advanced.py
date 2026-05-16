"""
Advanced Portfolio Analysis
BUY signals based on:
- Relative Strength vs NIFTY
- Volume Expansion
- Sector Strength
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
import pandas as pd
import time

# Portfolio with sector classification
PORTFOLIO = {
        # Banking
    'HDFCBANK': 'Banking',
    'ICICIBANK': 'Banking',
    'SBIN': 'Banking',

    # Information Technology
    'INFY': 'IT',
    'TCS': 'IT',
    'WIPRO': 'IT',

    # Energy / Oil & Gas
    'RELIANCE': 'Energy',
    'IOC': 'Energy',
    'OIL': 'Energy',

    # FMCG / Consumer Goods
    'ITC': 'FMCG',
    'HINDUNILVR': 'FMCG',
    'ASIANPAINT': 'FMCG',

    # Infrastructure / Engineering / Capital Goods
    'LT': 'Infrastructure',
    'HAL': 'Defence & Aerospace',

    # Automobile
    'TMCV': 'Automobile',
    'TMPV': 'Automobile',
    

    # Metals & Mining
    'VEDL': 'Metals & Mining',
    'SAIL': 'Metals & Mining',
    'TATASTEEL': 'Metals & Mining',

    # Power / Utilities
    'PFC': 'Power Finance',
    'ADANIPOWER': 'Power & Utilities',

    # Railway / Transportation
    'IRCTC': 'Railways & Tourism',

    # Conglomerates / Diversified
    'ADANIENT': 'Diversified',

    # Financial Services / NBFC / Fintech
    'JIOFIN': 'Financial Services',
}

print("="*90)
print("ADVANCED PORTFOLIO ANALYSIS")
print("Signals based on: Relative Strength | Volume Expansion | Sector Strength")
print("="*90)

fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')

# Step 1: Fetch NIFTY data for relative strength
print("\n📊 Fetching NIFTY 50 index data...")

# Try multiple NIFTY symbols
nifty_symbols = ['^NSEI', 'NIFTY', '^NSEBANK', 'NSEI.NS']
nifty_data = None

for nifty_symbol in nifty_symbols:
    try:
        print(f"   Trying {nifty_symbol}...", end=" ")
        # Fetch without exchange suffix for index
        if nifty_symbol.startswith('^'):
            data = fetcher.fetch_stock_data(nifty_symbol, exchange='', days=60)
        else:
            data = fetcher.fetch_stock_data(nifty_symbol, exchange='NSE', days=60)
        
        if data is not None and not data.empty and len(data) > 10:
            nifty_data = data
            print(f"✓ Success!")
            break
        else:
            print("✗ No data")
    except:
        print("✗ Failed")

if nifty_data is None or nifty_data.empty:
    print("\n⚠️  Could not fetch NIFTY data from any source.")
    print("   Relative Strength analysis will be disabled.")
    print("   Continuing with Volume and Sector analysis only...")
    nifty_data = None
else:
    nifty_data = MomentumIndicators.add_all_momentum_indicators(nifty_data)
    print(f"✓ NIFTY data fetched ({len(nifty_data)} days)")

# Step 2: Analyze each stock
print(f"\n📈 Analyzing {len(PORTFOLIO)} stocks...")
results = []
sector_data = {}

for i, (symbol, sector) in enumerate(PORTFOLIO.items(), 1):
    print(f"\n[{i}/{len(PORTFOLIO)}] {symbol} ({sector})...", end=" ")
    
    try:
        # Fetch stock data
        data = fetcher.fetch_stock_data(symbol, exchange='NSE', days=60)
        
        if data is None or data.empty:
            print("❌ No data")
            continue
        
        # Add indicators
        data = MomentumIndicators.add_all_momentum_indicators(data)
        data = TrendIndicators.add_all_trend_indicators(data)
        
        latest = data.iloc[-1]
        prev_5 = data.iloc[-6] if len(data) > 5 else data.iloc[0]
        prev_20 = data.iloc[-21] if len(data) > 20 else data.iloc[0]
        
        # === 1. RELATIVE STRENGTH vs NIFTY ===
        rs_score = 0
        rs_value = 0
        
        if nifty_data is not None and len(nifty_data) > 0:
            # Calculate returns
            stock_return_5d = ((latest['Close'] - prev_5['Close']) / prev_5['Close'] * 100)
            stock_return_20d = ((latest['Close'] - prev_20['Close']) / prev_20['Close'] * 100)
            
            nifty_latest = nifty_data.iloc[-1]
            nifty_prev_5 = nifty_data.iloc[-6] if len(nifty_data) > 5 else nifty_data.iloc[0]
            nifty_prev_20 = nifty_data.iloc[-21] if len(nifty_data) > 20 else nifty_data.iloc[0]
            
            nifty_return_5d = ((nifty_latest['Close'] - nifty_prev_5['Close']) / nifty_prev_5['Close'] * 100)
            nifty_return_20d = ((nifty_latest['Close'] - nifty_prev_20['Close']) / nifty_prev_20['Close'] * 100)
            
            # Relative strength
            rs_5d = stock_return_5d - nifty_return_5d
            rs_20d = stock_return_20d - nifty_return_20d
            
            rs_value = (rs_5d + rs_20d) / 2
            
            # Score based on relative strength
            if rs_value > 5:
                rs_score = 30  # Strong outperformance
            elif rs_value > 2:
                rs_score = 20  # Moderate outperformance
            elif rs_value > 0:
                rs_score = 10  # Slight outperformance
            elif rs_value > -2:
                rs_score = -10  # Slight underperformance
            else:
                rs_score = -20  # Underperformance
        
        # === 2. VOLUME EXPANSION ===
        volume_score = 0
        volume_ratio = 0
        
        if 'Volume' in data.columns:
            # Calculate average volume (20 days)
            avg_volume_20 = data['Volume'].tail(20).mean()
            current_volume = latest['Volume']
            
            volume_ratio = (current_volume / avg_volume_20) if avg_volume_20 > 0 else 1
            
            # Score based on volume expansion
            if volume_ratio > 2.0:
                volume_score = 25  # Very high volume
            elif volume_ratio > 1.5:
                volume_score = 20  # High volume
            elif volume_ratio > 1.2:
                volume_score = 15  # Above average
            elif volume_ratio > 0.8:
                volume_score = 5   # Normal
            else:
                volume_score = -10  # Low volume
        
        # === 3. MOMENTUM & TREND ===
        momentum_score = 0
        
        # RSI
        if latest['RSI'] > 60:
            momentum_score += 15
        elif latest['RSI'] > 50:
            momentum_score += 10
        elif latest['RSI'] < 40:
            momentum_score -= 10
        
        # SuperTrend
        if latest['SuperTrend_Direction'] == 1:
            momentum_score += 15
        else:
            momentum_score -= 15
        
        # Price vs MA
        if latest['Close'] > latest['SMA_20']:
            momentum_score += 10
        
        # === TOTAL SCORE ===
        total_score = rs_score + volume_score + momentum_score
        
        # Determine signal
        if total_score >= 60:
            signal = "STRONG BUY"
            emoji = "🟢"
        elif total_score >= 40:
            signal = "BUY"
            emoji = "🟢"
        elif total_score >= 0:
            signal = "HOLD"
            emoji = "🟡"
        elif total_score >= -40:
            signal = "SELL"
            emoji = "🔴"
        else:
            signal = "STRONG SELL"
            emoji = "🔴"
        
        # Store result
        result = {
            'Symbol': symbol,
            'Sector': sector,
            'Close': latest['Close'],
            'RSI': latest['RSI'],
            'Momentum': latest['Momentum_Score'],
            'RS_Score': rs_score,
            'RS_Value': rs_value,
            'Vol_Ratio': volume_ratio,
            'Vol_Score': volume_score,
            'Mom_Score': momentum_score,
            'Total_Score': total_score,
            'Signal': signal,
            'Emoji': emoji,
            'Trend': 'Bullish' if latest['SuperTrend_Direction'] == 1 else 'Bearish'
        }
        
        results.append(result)
        
        # Track sector performance
        if sector not in sector_data:
            sector_data[sector] = []
        sector_data[sector].append(total_score)
        
        print(f"✓ Score: {total_score}")
        time.sleep(0.5)
        
    except Exception as e:
        print(f"❌ {str(e)[:40]}")

if not results:
    print("\n❌ No data fetched.")
    exit()

# Create DataFrame
df = pd.DataFrame(results)
df = df.sort_values('Total_Score', ascending=False)

# Calculate sector strength
sector_strength = {}
for sector, scores in sector_data.items():
    sector_strength[sector] = sum(scores) / len(scores) if scores else 0

# Display Results
print("\n" + "="*90)
print("DETAILED ANALYSIS")
print("="*90)
print()

for _, row in df.iterrows():
    sector_avg = sector_strength.get(row['Sector'], 0)
    sector_status = "🔥" if sector_avg > 30 else "📈" if sector_avg > 0 else "📉"
    
    print(f"{row['Emoji']} {row['Symbol']:12} {row['Sector']:15} ₹{row['Close']:8.2f}")
    print(f"   RS: {row['RS_Value']:+6.2f}% ({row['RS_Score']:+3}) | "
          f"Vol: {row['Vol_Ratio']:4.2f}x ({row['Vol_Score']:+3}) | "
          f"Mom: {row['Mom_Score']:+3} | "
          f"Total: {row['Total_Score']:3} | "
          f"{row['Signal']}")
    print(f"   Sector Strength: {sector_status} {sector_avg:+.1f}")
    print()

# Sector Analysis
print("="*90)
print("SECTOR STRENGTH ANALYSIS")
print("="*90)

sorted_sectors = sorted(sector_strength.items(), key=lambda x: x[1], reverse=True)

for sector, strength in sorted_sectors:
    if strength > 30:
        status = "🔥 VERY STRONG"
    elif strength > 15:
        status = "📈 STRONG"
    elif strength > 0:
        status = "➡️  NEUTRAL"
    elif strength > -15:
        status = "📉 WEAK"
    else:
        status = "❄️  VERY WEAK"
    
    stocks_in_sector = [r['Symbol'] for r in results if r['Sector'] == sector]
    print(f"\n{status:20} {sector:15} (Avg Score: {strength:+6.1f})")
    print(f"   Stocks: {', '.join(stocks_in_sector)}")

# Buy Recommendations - STRICT CRITERIA
print("\n" + "="*90)
print("🎯 BUY RECOMMENDATIONS (STRICT CRITERIA)")
print("="*90)

# Filter stocks that meet ALL three criteria
qualified_buys = df[
    (df['RS_Value'] > 0) &           # Positive relative strength vs NIFTY
    (df['Vol_Ratio'] > 1.5) &        # Volume expansion >1.5x
    (df['Total_Score'] > 40)         # Good overall score
].copy()

# Further filter by sector strength
strong_sector_buys = []
weak_sector_buys = []

for _, row in qualified_buys.iterrows():
    sector_avg = sector_strength.get(row['Sector'], 0)
    if sector_avg > 15:  # Strong sector
        strong_sector_buys.append(row)
    else:
        weak_sector_buys.append(row)

if strong_sector_buys:
    print("\n🟢 STRONG BUY - All 3 Criteria Met + Strong Sector:")
    print("="*90)
    print("✓ Positive Relative Strength vs NIFTY")
    print("✓ Volume Expansion >1.5x average")
    print("✓ Stock in Strong Sector")
    print()
    
    for row in strong_sector_buys:
        sector_avg = sector_strength.get(row['Sector'], 0)
        
        print(f"🟢 {row['Symbol']:12} - STRONG BUY")
        print(f"   Price: ₹{row['Close']:.2f}")
        print(f"   ✓ Relative Strength: {row['RS_Value']:+.2f}% vs NIFTY (Outperforming)")
        print(f"   ✓ Volume: {row['Vol_Ratio']:.2f}x average (Expansion)")
        print(f"   ✓ Sector: {row['Sector']} (Strength: {sector_avg:+.1f} - Strong)")
        print(f"   Momentum Score: {row['Momentum']:.1f}/100")
        print(f"   Total Score: {row['Total_Score']}")
        print()

if weak_sector_buys:
    print("\n🟡 CONDITIONAL BUY - 2 of 3 Criteria Met (Weak Sector):")
    print("="*90)
    print("✓ Positive Relative Strength vs NIFTY")
    print("✓ Volume Expansion >1.5x average")
    print("⚠️  Stock in Weak/Neutral Sector - Use Caution")
    print()
    
    for row in weak_sector_buys:
        sector_avg = sector_strength.get(row['Sector'], 0)
        
        print(f"🟡 {row['Symbol']:12} - CONDITIONAL BUY")
        print(f"   Price: ₹{row['Close']:.2f}")
        print(f"   ✓ Relative Strength: {row['RS_Value']:+.2f}% vs NIFTY")
        print(f"   ✓ Volume: {row['Vol_Ratio']:.2f}x average")
        print(f"   ⚠️  Sector: {row['Sector']} (Strength: {sector_avg:+.1f} - Weak)")
        print(f"   Note: Consider waiting for sector to strengthen")
        print()

if not strong_sector_buys and not weak_sector_buys:
    print("\n⚠️  NO STOCKS MEET ALL CRITERIA")
    print("="*90)
    print("\nRequired Criteria:")
    print("1. Positive Relative Strength vs NIFTY (RS > 0%)")
    print("2. Volume Expansion >1.5x average")
    print("3. Strong Sector (Sector Avg > 15)")
    print("\nStocks close to qualifying:")
    
    # Show stocks that meet 2 out of 3 criteria
    near_miss = df[
        ((df['RS_Value'] > 0) & (df['Vol_Ratio'] > 1.5)) |
        ((df['RS_Value'] > 0) & (df['Total_Score'] > 30)) |
        ((df['Vol_Ratio'] > 1.5) & (df['Total_Score'] > 30))
    ].head(5)
    
    if not near_miss.empty:
        print()
        for _, row in near_miss.iterrows():
            sector_avg = sector_strength.get(row['Sector'], 0)
            criteria_met = []
            if row['RS_Value'] > 0:
                criteria_met.append("✓ RS")
            else:
                criteria_met.append("✗ RS")
            if row['Vol_Ratio'] > 1.5:
                criteria_met.append("✓ Vol")
            else:
                criteria_met.append("✗ Vol")
            if sector_avg > 15:
                criteria_met.append("✓ Sector")
            else:
                criteria_met.append("✗ Sector")
            
            print(f"   {row['Symbol']:12} {' | '.join(criteria_met)}")
    else:
        print("\n   No stocks are close to qualifying. Market conditions may be weak.")

# Statistics
print("="*90)
print("PORTFOLIO STATISTICS")
print("="*90)

signal_counts = df['Signal'].value_counts()
print(f"\nTotal Stocks: {len(df)}")
print(f"Strong Buy: {signal_counts.get('STRONG BUY', 0)}")
print(f"Buy: {signal_counts.get('BUY', 0)}")
print(f"Hold: {signal_counts.get('HOLD', 0)}")
print(f"Sell: {signal_counts.get('SELL', 0)}")
print(f"Strong Sell: {signal_counts.get('STRONG SELL', 0)}")

print(f"\nAverage Relative Strength: {df['RS_Value'].mean():+.2f}%")
print(f"Average Volume Ratio: {df['Vol_Ratio'].mean():.2f}x")
print(f"Average Total Score: {df['Total_Score'].mean():.1f}")

# Top Sector
if sorted_sectors:
    top_sector = sorted_sectors[0]
    print(f"\n🏆 Strongest Sector: {top_sector[0]} ({top_sector[1]:+.1f})")

print("\n" + "="*90)
print("Analysis Complete!")
print("="*90)
print("\nKey Insights:")
print("• Focus on stocks with positive relative strength vs NIFTY")
print("• Look for volume expansion (>1.5x average)")
print("• Prefer stocks in strong sectors")
print("• Combine all three factors for best results")

# Made with Bob
