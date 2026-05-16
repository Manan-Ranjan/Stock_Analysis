"""
Diagnostic tool to see what signals are being generated
Helps understand why no trades are executed
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from momentum_trading.data.fetcher import DataFetcher
from momentum_trading.indicators.momentum import MomentumIndicators
from momentum_trading.indicators.trend import TrendIndicators
import pandas as pd
from datetime import datetime, timedelta

def diagnose_stock_signals(symbol, days=90):
    """Show signal scores for a stock over time"""
    
    print(f"\n{'='*80}")
    print(f"SIGNAL DIAGNOSIS: {symbol}")
    print(f"{'='*80}")
    
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
    
    # Fetch data
    data = fetcher.fetch_stock_data(symbol, exchange='NSE', days=days+60)
    if data is None or data.empty:
        print(f"❌ No data for {symbol}")
        return
    
    # Add indicators
    data = MomentumIndicators.add_all_momentum_indicators(data)
    data = TrendIndicators.add_all_trend_indicators(data)
    
    # Fetch NIFTY
    nifty_data = None
    for nifty_symbol in ['^NSEI', 'NIFTY']:
        try:
            nifty_data = fetcher.fetch_stock_data(nifty_symbol, exchange='', days=days+60)
            if nifty_data is not None and not nifty_data.empty:
                nifty_data = MomentumIndicators.add_all_momentum_indicators(nifty_data)
                break
        except:
            continue
    
    # Calculate scores for last 30 days
    scores = []
    
    for i in range(max(20, len(data)-30), len(data)):
        if i < 20:
            continue
            
        latest = data.iloc[i]
        prev_5 = data.iloc[i-5] if i >= 5 else data.iloc[0]
        prev_20 = data.iloc[i-20] if i >= 20 else data.iloc[0]
        
        # RS Score
        rs_score = 0
        if nifty_data is not None and len(nifty_data) > i:
            stock_return_5d = ((latest['Close'] - prev_5['Close']) / prev_5['Close'] * 100)
            nifty_latest = nifty_data.iloc[i]
            nifty_prev_5 = nifty_data.iloc[i-5] if i >= 5 else nifty_data.iloc[0]
            nifty_return_5d = ((nifty_latest['Close'] - nifty_prev_5['Close']) / nifty_prev_5['Close'] * 100)
            rs_value = stock_return_5d - nifty_return_5d
            
            if rs_value > 5:
                rs_score = 30
            elif rs_value > 2:
                rs_score = 20
            elif rs_value > 0:
                rs_score = 10
            elif rs_value > -2:
                rs_score = -10
            else:
                rs_score = -20
        
        # Volume Score
        volume_score = 0
        if 'Volume' in data.columns:
            avg_volume = data['Volume'].iloc[i-20:i].mean()
            vol_ratio = latest['Volume'] / avg_volume if avg_volume > 0 else 1
            if vol_ratio > 2.0:
                volume_score = 25
            elif vol_ratio > 1.5:
                volume_score = 20
            elif vol_ratio > 1.2:
                volume_score = 15
            elif vol_ratio > 0.8:
                volume_score = 5
            else:
                volume_score = -10
        
        # Momentum Score
        momentum_score = 0
        if latest['RSI'] > 60:
            momentum_score += 15
        elif latest['RSI'] > 50:
            momentum_score += 10
        elif latest['RSI'] < 40:
            momentum_score -= 10
        
        if latest['SuperTrend_Direction'] == 1:
            momentum_score += 15
        else:
            momentum_score -= 15
        
        if latest['Close'] > latest['SMA_20']:
            momentum_score += 10
        
        total_score = rs_score + volume_score + momentum_score
        
        # Determine signal
        if total_score >= 60:
            signal = "STRONG BUY"
        elif total_score >= 40:
            signal = "BUY"
        elif total_score >= 20:
            signal = "WEAK BUY"
        elif total_score >= 0:
            signal = "HOLD"
        else:
            signal = "SELL"
        
        date = pd.to_datetime(data.index[i])
        scores.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Close': latest['Close'],
            'RS': rs_score,
            'Vol': volume_score,
            'Mom': momentum_score,
            'Total': total_score,
            'Signal': signal
        })
    
    # Display results
    df = pd.DataFrame(scores)
    
    print(f"\nLast 30 Days Signal History:")
    print(df.to_string(index=False))
    
    # Statistics
    print(f"\n{'='*80}")
    print("STATISTICS")
    print(f"{'='*80}")
    print(f"Average Score: {df['Total'].mean():.1f}")
    print(f"Max Score: {df['Total'].max()}")
    print(f"Min Score: {df['Total'].min()}")
    print(f"\nSignal Distribution:")
    print(df['Signal'].value_counts().to_string())
    
    # Check for BUY signals
    buy_signals = df[df['Signal'].isin(['BUY', 'STRONG BUY', 'WEAK BUY'])]
    if len(buy_signals) > 0:
        print(f"\n✓ Found {len(buy_signals)} BUY signals in last 30 days")
        print("\nBest opportunities:")
        print(buy_signals.nlargest(5, 'Total')[['Date', 'Total', 'Signal']].to_string(index=False))
    else:
        print(f"\n⚠️  No BUY signals in last 30 days")
        print("\nReasons:")
        print(f"  - Avg RS Score: {df['RS'].mean():.1f} (need positive for BUY)")
        print(f"  - Avg Vol Score: {df['Vol'].mean():.1f} (need >15 for BUY)")
        print(f"  - Avg Mom Score: {df['Mom'].mean():.1f} (need >10 for BUY)")


if __name__ == "__main__":
    # Diagnose multiple stocks
    stocks = ['TATASTEEL', 'SAIL', 'ADANIENT', 'ASIANPAINT', 'ITC']
    
    print("="*80)
    print("SIGNAL DIAGNOSTIC TOOL")
    print("="*80)
    print("\nAnalyzing signal generation for last 30 days...")
    
    for stock in stocks:
        diagnose_stock_signals(stock, days=90)
    
    print(f"\n{'='*80}")
    print("DIAGNOSIS COMPLETE")
    print(f"{'='*80}")
    print("\nIf no BUY signals found:")
    print("1. Market may be in downtrend - this is normal")
    print("2. Strategy is working correctly by avoiding bad trades")
    print("3. Try backtesting during bull market periods")
    print("4. Or adjust thresholds in backtest_strategy.py")

# Made with Bob
