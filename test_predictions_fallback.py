"""
Test script to verify the predictions page data fallback system
"""
import sys
import os
sys.path.insert(0, 'frontend')

from utils.data_helper import fetch_stock_data
import pandas as pd

def test_data_fallback():
    """Test data fetching with fallback to CSV files"""
    
    print("=" * 60)
    print("Testing Data Fallback System")
    print("=" * 60)
    
    # Test stocks that should have CSV files
    test_stocks = ['HDFCBANK', 'RELIANCE', 'INFY', 'TCS', 'ICICIBANK']
    
    for symbol in test_stocks:
        print(f"\n📊 Testing {symbol}...")
        
        try:
            data, source = fetch_stock_data(symbol, period="60d")
            
            if data is not None and not data.empty:
                print(f"✅ SUCCESS - Data loaded from: {source}")
                print(f"   Rows: {len(data)}")
                print(f"   Date range: {data['Date'].min()} to {data['Date'].max()}")
                print(f"   Latest close: ₹{data['Close'].iloc[-1]:.2f}")
                
                # Check required columns
                required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                missing_cols = [col for col in required_cols if col not in data.columns]
                if missing_cols:
                    print(f"   ⚠️  Missing columns: {missing_cols}")
                else:
                    print(f"   ✓ All required columns present")
            else:
                print(f"❌ FAILED - No data returned")
                
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_data_fallback()

# Made with Bob
