"""
Test script to diagnose data fetching issues
Run this to see what's working and what's not
"""

import sys
import os

print("="*70)
print("DATA FETCHING DIAGNOSTIC TEST")
print("="*70)

# Test 1: Check if yfinance is installed
print("\n1. Testing yfinance installation...")
try:
    import yfinance as yf
    print("✓ yfinance is installed")
except ImportError as e:
    print(f"✗ yfinance not found: {e}")
    print("  Install with: pip install yfinance")
    sys.exit(1)

# Test 2: Try fetching data with different formats
print("\n2. Testing data fetch with different symbol formats...")

symbols_to_test = [
    ("HDFCBANK.NS", "NSE format"),
    ("HDFCBANK.BO", "BSE format"),
    ("RELIANCE.NS", "Reliance NSE"),
    ("TCS.NS", "TCS NSE"),
]

successful_fetches = []

for symbol, description in symbols_to_test:
    try:
        print(f"\n   Testing {symbol} ({description})...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")
        
        if data is not None and not data.empty:
            print(f"   ✓ SUCCESS! Fetched {len(data)} days of data")
            print(f"     Latest close: ₹{data['Close'].iloc[-1]:.2f}")
            successful_fetches.append(symbol)
        else:
            print(f"   ✗ No data returned")
    except Exception as e:
        print(f"   ✗ Error: {str(e)[:100]}")

# Test 3: Check momentum_trading module
print("\n3. Testing momentum_trading module...")
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from momentum_trading.data.fetcher import DataFetcher
    print("✓ momentum_trading.data.fetcher found")
    
    try:
        fetcher = DataFetcher()
        print("✓ DataFetcher initialized")
        
        # Try fetching
        print("   Trying to fetch HDFCBANK...")
        data = fetcher.fetch_stock_data('HDFCBANK', exchange='NSE', days=5)
        if data is not None and not data.empty:
            print(f"   ✓ SUCCESS! Fetched {len(data)} days")
        else:
            print("   ✗ No data returned")
    except Exception as e:
        print(f"   ✗ Error using DataFetcher: {str(e)[:100]}")
        
except ImportError as e:
    print(f"✗ momentum_trading module not found: {e}")
    print("  This is OK - we'll use yfinance directly")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

if successful_fetches:
    print(f"\n✓ Successfully fetched data for {len(successful_fetches)} symbols:")
    for symbol in successful_fetches:
        print(f"  - {symbol}")
    print("\n💡 RECOMMENDATION: Use these symbol formats in the app")
    print("   Example: HDFCBANK.NS, RELIANCE.NS, TCS.NS")
else:
    print("\n✗ Could not fetch data for any symbols")
    print("\n🔍 POSSIBLE ISSUES:")
    print("  1. No internet connection")
    print("  2. Yahoo Finance is down or rate-limiting")
    print("  3. Firewall blocking requests")
    print("\n💡 TRY:")
    print("  - Check your internet connection")
    print("  - Wait a few minutes and try again")
    print("  - Try from a different network")

print("\n" + "="*70)

# Made with Bob
