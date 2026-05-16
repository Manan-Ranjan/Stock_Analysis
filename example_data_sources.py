"""
Example script demonstrating multi-source data fetching
Shows how to use Google Finance and Yahoo Finance with fallback
"""

from data_fetcher import DataFetcher, DataSourceConfig
import json


def example_1_google_primary():
    """Example 1: Use Google Finance as primary source"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Google Finance Primary, Yahoo Finance Fallback")
    print("="*70)
    
    fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
    
    # Fetch data for HDFC Bank
    print("\nFetching HDFCBANK data...")
    data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)
    
    if data is not None:
        print(f"\n✓ Successfully fetched {len(data)} records")
        print(f"Data source: {data['Source'].iloc[0]}")
        print(f"\nLatest data:")
        print(data.tail(3))
    else:
        print("✗ Failed to fetch data")


def example_2_yahoo_primary():
    """Example 2: Use Yahoo Finance as primary source"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Yahoo Finance Primary, Google Finance Fallback")
    print("="*70)
    
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
    
    # Fetch data for Reliance
    print("\nFetching RELIANCE data...")
    data = fetcher.fetch_stock_data('RELIANCE', 'NSE', days=30)
    
    if data is not None:
        print(f"\n✓ Successfully fetched {len(data)} records")
        print(f"Data source: {data['Source'].iloc[0]}")
        print(f"\nData columns: {list(data.columns)}")
        print(f"\nLatest closing prices:")
        print(data[['Date', 'Close']].tail(5))
    else:
        print("✗ Failed to fetch data")


def example_3_current_price():
    """Example 3: Get current price quickly"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Quick Current Price Lookup")
    print("="*70)
    
    fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
    
    stocks = ['HDFCBANK', 'RELIANCE', 'TCS', 'INFY', 'ICICIBANK']
    
    print("\nCurrent Prices:")
    print("-" * 40)
    for symbol in stocks:
        price = fetcher.get_current_price(symbol, 'NSE')
        if price:
            print(f"{symbol:12} : ₹{price:,.2f}")
        else:
            print(f"{symbol:12} : Data not available")


def example_4_multiple_stocks():
    """Example 4: Fetch multiple stocks at once"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Fetch Multiple Stocks")
    print("="*70)
    
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='google')
    
    stocks_list = [
        ('HDFCBANK', 'HDFC Bank'),
        ('RELIANCE', 'Reliance Industries'),
        ('TCS', 'Tata Consultancy Services'),
        ('INFY', 'Infosys')
    ]
    
    results = fetcher.fetch_multiple_stocks(stocks_list, exchange='NSE', days=30)
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    for symbol, info in results.items():
        data = info['data']
        latest_close = data['Close'].iloc[-1] if 'Close' in data.columns else 'N/A'
        print(f"\n{info['name']} ({symbol}):")
        print(f"  Records: {len(data)}")
        print(f"  Latest Close: ₹{latest_close}")
        print(f"  Data Source: {data['Source'].iloc[0]}")


def example_5_configuration():
    """Example 5: Using configuration manager"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Configuration Manager")
    print("="*70)
    
    # Load configuration
    config = DataSourceConfig()
    print("\nCurrent Configuration:")
    print(json.dumps(config.config, indent=2))
    
    # Update configuration
    print("\nUpdating configuration...")
    config.update_config(
        primary_source='yahoo',
        fallback_source='google',
        days=60
    )
    
    print("\nUpdated Configuration:")
    print(json.dumps(config.config, indent=2))
    
    # Use configured fetcher
    fetcher = config.get_fetcher()
    print("\nFetching data with configured settings...")
    data = fetcher.fetch_stock_data('TATAMOTORS', 'NSE', days=config.config['days'])
    
    if data is not None:
        print(f"\n✓ Fetched {len(data)} days of data for TATAMOTORS")


def example_6_comparison():
    """Example 6: Compare data from both sources"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Compare Google vs Yahoo Data")
    print("="*70)
    
    symbol = 'HDFCBANK'
    
    # Fetch from Google
    print(f"\nFetching {symbol} from Google Finance...")
    google_fetcher = DataFetcher(primary_source='google', fallback_source='google')
    google_data = google_fetcher.fetch_stock_data(symbol, 'NSE', days=1)
    
    # Fetch from Yahoo
    print(f"\nFetching {symbol} from Yahoo Finance...")
    yahoo_fetcher = DataFetcher(primary_source='yahoo', fallback_source='yahoo')
    yahoo_data = yahoo_fetcher.fetch_stock_data(symbol, 'NSE', days=1)
    
    print("\n" + "-"*70)
    print("COMPARISON")
    print("-"*70)
    
    if google_data is not None and not google_data.empty:
        print(f"\nGoogle Finance:")
        print(f"  Close Price: ₹{google_data['Close'].iloc[-1]:,.2f}")
        print(f"  Data Points: {len(google_data)}")
    
    if yahoo_data is not None and not yahoo_data.empty:
        print(f"\nYahoo Finance:")
        print(f"  Close Price: ₹{yahoo_data['Close'].iloc[-1]:,.2f}")
        print(f"  Data Points: {len(yahoo_data)}")
        print(f"  Volume: {yahoo_data['Volume'].iloc[-1]:,}")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("MULTI-SOURCE STOCK DATA FETCHER - EXAMPLES")
    print("="*70)
    
    examples = [
        ("Google Primary", example_1_google_primary),
        ("Yahoo Primary", example_2_yahoo_primary),
        ("Current Prices", example_3_current_price),
        ("Multiple Stocks", example_4_multiple_stocks),
        ("Configuration", example_5_configuration),
        ("Source Comparison", example_6_comparison)
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...")
    print("(This may take a few minutes due to rate limiting)")
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in {name}: {e}")
        
        # Small delay between examples
        import time
        time.sleep(2)
    
    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED")
    print("="*70)
    print("\nFor more information, see README_DATA_SOURCES.md")


if __name__ == "__main__":
    main()

# Made with Bob
