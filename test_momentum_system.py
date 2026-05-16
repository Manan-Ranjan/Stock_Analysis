"""
Test Script for Momentum Trading System
Run this to test all components
"""

import sys
import os

# Add momentum_trading to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'momentum_trading'))

print("="*80)
print("MOMENTUM TRADING SYSTEM - COMPREHENSIVE TEST")
print("="*80)

# Test 1: Check Dependencies
print("\n" + "="*80)
print("TEST 1: Checking Dependencies")
print("="*80)

dependencies = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'yfinance': 'yfinance',
    'nsepy': 'nsepy',
    'requests': 'requests',
    'beautifulsoup4': 'bs4',
    'ta': 'ta',
    'plotly': 'plotly',
    'matplotlib': 'matplotlib'
}

missing_deps = []
for name, import_name in dependencies.items():
    try:
        __import__(import_name)
        print(f"✓ {name} - OK")
    except ImportError:
        print(f"✗ {name} - MISSING")
        missing_deps.append(name)

if missing_deps:
    print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
    print(f"Install with: pip install {' '.join(missing_deps)}")
    print("\nOr install all at once:")
    print("pip install -r momentum_trading/requirements.txt")
else:
    print("\n✓ All dependencies installed!")

# Test 2: NSEpy Data Fetcher
print("\n" + "="*80)
print("TEST 2: NSEpy Data Fetcher")
print("="*80)

try:
    from momentum_trading.data.nse_fetcher import NSEDataFetcher
    from datetime import datetime, timedelta
    
    nse = NSEDataFetcher()
    print("✓ NSEDataFetcher initialized")
    
    # Test stock data
    print("\nFetching HDFCBANK stock data (last 5 days)...")
    stock_data = nse.fetch_stock_data('HDFCBANK', days=5)
    
    if stock_data is not None and not stock_data.empty:
        print(f"✓ Successfully fetched {len(stock_data)} days of data")
        print(f"\nColumns: {stock_data.columns.tolist()}")
        print(f"\nLatest data:")
        print(stock_data[['Date', 'Close', 'Volume']].tail(3))
    else:
        print("⚠️  No data returned (NSE might be closed or network issue)")
    
    # Test futures data with OI
    print("\n" + "-"*80)
    print("Fetching RELIANCE futures data with Open Interest...")
    futures_data = nse.fetch_futures_data('RELIANCE', days=5)
    
    if futures_data is not None and not futures_data.empty:
        print(f"✓ Successfully fetched futures data")
        if 'OI' in futures_data.columns:
            print(f"✓ Open Interest data available")
            print(f"\nLatest OI data:")
            print(futures_data[['Date', 'Close', 'OI', 'OI_Change']].tail(3))
        else:
            print("⚠️  OI columns not found")
    else:
        print("⚠️  No futures data returned")
    
    # Test OI Analysis
    print("\n" + "-"*80)
    print("Testing Open Interest Analysis...")
    oi_analysis = nse.get_oi_analysis('RELIANCE')
    
    if oi_analysis:
        print("✓ OI Analysis successful")
        print(f"\nAnalysis Results:")
        print(f"  Signal: {oi_analysis.get('signal', 'N/A')}")
        if 'interpretation' in oi_analysis:
            print(f"  Type: {oi_analysis['interpretation'].get('type', 'N/A')}")
            print(f"  Description: {oi_analysis['interpretation'].get('description', 'N/A')}")
    else:
        print("⚠️  OI Analysis returned empty")
    
    print("\n✓ NSEpy tests completed")
    
except Exception as e:
    print(f"✗ NSEpy test failed: {e}")
    print("Note: NSEpy requires active market hours for some data")

# Test 3: Unified Data Fetcher
print("\n" + "="*80)
print("TEST 3: Unified Data Fetcher")
print("="*80)

try:
    from momentum_trading.data.fetcher import DataFetcher
    
    # Test with Yahoo Finance (more reliable for testing)
    print("Testing with Yahoo Finance as primary source...")
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
    print("✓ DataFetcher initialized")
    
    print("\nFetching HDFCBANK data...")
    data = fetcher.fetch_stock_data('HDFCBANK', exchange='NSE', days=30)
    
    if data is not None and not data.empty:
        print(f"✓ Successfully fetched {len(data)} days of data")
        print(f"\nColumns: {data.columns.tolist()}")
        print(f"\nFirst 3 rows:")
        print(data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].head(3))
        print(f"\nLast 3 rows:")
        print(data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail(3))
    else:
        print("✗ Failed to fetch data")
    
    print("\n✓ Unified Data Fetcher tests completed")
    
except Exception as e:
    print(f"✗ Unified Data Fetcher test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Momentum Indicators
print("\n" + "="*80)
print("TEST 4: Momentum Indicators")
print("="*80)

try:
    from momentum_trading.indicators.momentum import MomentumIndicators
    import pandas as pd
    import numpy as np
    
    # Create sample data
    print("Creating sample data...")
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': 100 + np.random.randn(100).cumsum(),
        'High': 102 + np.random.randn(100).cumsum(),
        'Low': 98 + np.random.randn(100).cumsum(),
        'Close': 100 + np.random.randn(100).cumsum(),
        'Volume': np.random.randint(1000000, 5000000, 100)
    })
    print(f"✓ Created sample data with {len(sample_data)} rows")
    
    # Test individual indicators
    print("\nTesting individual indicators...")
    
    print("  - RSI...", end=" ")
    rsi = MomentumIndicators.calculate_rsi(sample_data)
    print(f"✓ (Latest: {rsi.iloc[-1]:.2f})")
    
    print("  - ROC...", end=" ")
    roc = MomentumIndicators.calculate_roc(sample_data)
    print(f"✓ (Latest: {roc.iloc[-1]:.2f})")
    
    print("  - Stochastic...", end=" ")
    stoch_k, stoch_d = MomentumIndicators.calculate_stochastic(sample_data)
    print(f"✓ (K: {stoch_k.iloc[-1]:.2f}, D: {stoch_d.iloc[-1]:.2f})")
    
    print("  - MACD...", end=" ")
    macd, signal, hist = MomentumIndicators.calculate_macd(sample_data)
    print(f"✓ (MACD: {macd.iloc[-1]:.2f})")
    
    # Test adding all indicators
    print("\nAdding all momentum indicators...")
    result = MomentumIndicators.add_all_momentum_indicators(sample_data)
    
    new_columns = [col for col in result.columns if col not in sample_data.columns]
    print(f"✓ Added {len(new_columns)} indicator columns")
    print(f"  Indicators: {', '.join(new_columns)}")
    
    print("\nLatest indicator values:")
    print(result[['Date', 'Close', 'RSI', 'ROC', 'MACD', 'Momentum_Score']].tail(3))
    
    print("\n✓ Momentum Indicators tests completed")
    
except Exception as e:
    print(f"✗ Momentum Indicators test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Trend Indicators
print("\n" + "="*80)
print("TEST 5: Trend Indicators")
print("="*80)

try:
    from momentum_trading.indicators.trend import TrendIndicators
    
    print("Testing trend indicators on sample data...")
    
    # Test SuperTrend
    print("\n  - SuperTrend...", end=" ")
    supertrend, direction = TrendIndicators.calculate_supertrend(sample_data)
    print(f"✓ (Value: {supertrend.iloc[-1]:.2f}, Direction: {direction.iloc[-1]})")
    
    # Test Moving Averages
    print("  - SMA...", end=" ")
    sma = TrendIndicators.calculate_sma(sample_data, period=20)
    print(f"✓ (SMA20: {sma.iloc[-1]:.2f})")
    
    print("  - EMA...", end=" ")
    ema = TrendIndicators.calculate_ema(sample_data, period=20)
    print(f"✓ (EMA20: {ema.iloc[-1]:.2f})")
    
    # Test ADX
    print("  - ADX...", end=" ")
    adx, plus_di, minus_di = TrendIndicators.calculate_adx(sample_data)
    print(f"✓ (ADX: {adx.iloc[-1]:.2f})")
    
    # Test adding all indicators
    print("\nAdding all trend indicators...")
    result = TrendIndicators.add_all_trend_indicators(sample_data)
    
    new_columns = [col for col in result.columns if col not in sample_data.columns]
    print(f"✓ Added {len(new_columns)} indicator columns")
    print(f"  Indicators: {', '.join(new_columns[:10])}...")
    
    print("\nLatest trend indicator values:")
    print(result[['Date', 'Close', 'SuperTrend', 'SuperTrend_Direction', 'SMA_20', 'ADX']].tail(3))
    
    print("\n✓ Trend Indicators tests completed")
    
except Exception as e:
    print(f"✗ Trend Indicators test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Complete Workflow
print("\n" + "="*80)
print("TEST 6: Complete Workflow (Data + Indicators)")
print("="*80)

try:
    print("Running complete workflow...")
    
    # Fetch real data
    print("\n1. Fetching real stock data...")
    fetcher = DataFetcher(primary_source='yahoo')
    stock_data = fetcher.fetch_stock_data('INFY', exchange='NSE', days=60)
    
    if stock_data is not None and not stock_data.empty:
        print(f"   ✓ Fetched {len(stock_data)} days of INFY data")
        
        # Add momentum indicators
        print("\n2. Adding momentum indicators...")
        stock_data = MomentumIndicators.add_all_momentum_indicators(stock_data)
        print(f"   ✓ Momentum indicators added")
        
        # Add trend indicators
        print("\n3. Adding trend indicators...")
        stock_data = TrendIndicators.add_all_trend_indicators(stock_data)
        print(f"   ✓ Trend indicators added")
        
        # Display results
        print("\n4. Analysis Results:")
        print(f"   Total columns: {len(stock_data.columns)}")
        
        latest = stock_data.iloc[-1]
        print(f"\n   Latest Analysis for INFY ({latest['Date']}):")
        print(f"   Close Price: ₹{latest['Close']:.2f}")
        print(f"   RSI: {latest['RSI']:.2f}")
        print(f"   Momentum Score: {latest['Momentum_Score']:.2f}")
        print(f"   SuperTrend: ₹{latest['SuperTrend']:.2f}")
        print(f"   Trend Direction: {'Bullish' if latest['SuperTrend_Direction'] == 1 else 'Bearish'}")
        print(f"   ADX: {latest['ADX']:.2f}")
        
        # Simple signal
        signal = "BUY" if (latest['RSI'] > 50 and latest['SuperTrend_Direction'] == 1 and latest['Momentum_Score'] > 60) else \
                 "SELL" if (latest['RSI'] < 50 and latest['SuperTrend_Direction'] == -1 and latest['Momentum_Score'] < 40) else \
                 "HOLD"
        
        print(f"\n   📊 Simple Signal: {signal}")
        
        print("\n✓ Complete workflow test successful!")
    else:
        print("   ⚠️  Could not fetch stock data")
    
except Exception as e:
    print(f"✗ Complete workflow test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

print("""
✓ Tests completed!

Next Steps:
1. If any dependencies are missing, install them:
   pip install -r momentum_trading/requirements.txt

2. For NSEpy tests to work fully, run during market hours

3. To use the system:
   - See momentum_trading/README.md for detailed examples
   - Check ARCHITECTURE.md for system design
   - Run individual modules with: python -m momentum_trading.data.nse_fetcher

4. To implement remaining components:
   - Signals module (signal generation)
   - Risk management module
   - Backtesting engine
   - Reporting dashboard

5. For production use:
   - Set up proper configuration
   - Add error handling
   - Implement logging
   - Add database storage
""")

print("="*80)
print("Testing complete! Check output above for any issues.")
print("="*80)

# Made with Bob
