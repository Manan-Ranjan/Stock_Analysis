"""
Data Helper - Fetches stock data with multiple fallbacks
1. Try yfinance (live/recent data)
2. Fall back to local CSV files (your existing data)
3. Provide helpful error messages
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import yfinance as yf


def fetch_stock_data_with_fallback(symbol, days=60, period=None):
    """
    Fetch stock data with multiple fallback options
    
    Args:
        symbol: Stock symbol (e.g., 'HDFCBANK' or 'HDFCBANK.NS')
        days: Number of days of historical data (default: 60)
        period: Period string like '1mo', '60d', etc. (overrides days if provided)
    
    Returns:
        Tuple of (DataFrame, source_string)
        DataFrame with columns: Date, Open, High, Low, Close, Volume
    """
    
    # Convert period to days if provided
    if period:
        if period.endswith('d'):
            days = int(period[:-1])
        elif period.endswith('mo'):
            days = int(period[:-2]) * 30
        elif period.endswith('y'):
            days = int(period[:-1]) * 365
    
    # Clean symbol (remove .NS or .BO if present)
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    # Method 1: Try yfinance with .NS suffix
    try:
        print(f"Attempting to fetch {clean_symbol}.NS from Yahoo Finance...")
        ticker = yf.Ticker(f"{clean_symbol}.NS")
        data = ticker.history(period=f"{days}d")
        
        if not data.empty and len(data) > 5:
            data = data.reset_index()
            data = data.rename(columns={'index': 'Date'})
            # Remove timezone information for Prophet compatibility
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            print(f"✓ Successfully fetched {len(data)} days from Yahoo Finance")
            return data, "Yahoo Finance (Live)"
    except Exception as e:
        print(f"Yahoo Finance failed: {e}")
    
    # Method 2: Try local CSV file
    try:
        csv_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'stock_data', 
            f'{clean_symbol}_data.csv'
        )
        
        if os.path.exists(csv_path):
            print(f"Found local CSV file: {csv_path}")
            data = pd.read_csv(csv_path)
            
            # Ensure Date column exists
            if 'Date' not in data.columns and 'date' in data.columns:
                data = data.rename(columns={'date': 'Date'})
            
            # Convert Date to datetime and remove timezone
            data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            
            # Get last N days
            data = data.tail(days)
            
            if not data.empty:
                print(f"✓ Successfully loaded {len(data)} days from local CSV")
                return data, f"Local CSV (Last updated: {data['Date'].max().strftime('%Y-%m-%d')})"
    except Exception as e:
        print(f"Local CSV failed: {e}")
    
    # Method 3: Try without .NS suffix
    try:
        print(f"Attempting to fetch {clean_symbol} (without .NS)...")
        ticker = yf.Ticker(clean_symbol)
        data = ticker.history(period=f"{days}d")
        
        if not data.empty and len(data) > 5:
            data = data.reset_index()
            data = data.rename(columns={'index': 'Date'})
            # Remove timezone information for Prophet compatibility
            if 'Date' in data.columns:
                data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)
            print(f"✓ Successfully fetched {len(data)} days")
            return data, "Yahoo Finance"
    except Exception as e:
        print(f"Direct symbol fetch failed: {e}")
    
    # All methods failed
    return None, "Failed"


def get_available_stocks():
    """
    Get list of stocks available in local CSV files
    
    Returns:
        List of stock symbols
    """
    try:
        stock_data_dir = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 
            'stock_data'
        )
        
        if os.path.exists(stock_data_dir):
            csv_files = [f for f in os.listdir(stock_data_dir) if f.endswith('_data.csv')]
            stocks = [f.replace('_data.csv', '') for f in csv_files]
            return sorted(stocks)
    except:
        pass
    
    return []


def format_data_for_prophet(data):
    """
    Format data for Prophet (requires 'ds' and 'y' columns)
    
    Args:
        data: DataFrame with Date and Close columns
    
    Returns:
        DataFrame with ds and y columns
    """
    df = data[['Date', 'Close']].copy()
    df.columns = ['ds', 'y']
    return df


# Alias for convenience
fetch_stock_data = fetch_stock_data_with_fallback

# Made with Bob
