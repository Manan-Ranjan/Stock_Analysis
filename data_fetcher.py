"""
Multi-Source Stock Data Fetcher
Supports Google Finance (web scraping), Yahoo Finance, and Finnhub API with fallback mechanism
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import json
import re
import os


class DataFetcher:
    """
    Unified data fetcher supporting multiple sources:
    - Google Finance (web scraping)
    - Yahoo Finance (API)
    - Finnhub (API)
    """
    
    def __init__(self, primary_source='yahoo', fallback_source='finnhub', finnhub_api_key=None):
        """
        Initialize data fetcher with source preferences
        
        Args:
            primary_source: 'google', 'yahoo', or 'finnhub' (default: 'yahoo')
            fallback_source: 'google', 'yahoo', or 'finnhub' (default: 'finnhub')
            finnhub_api_key: API key for Finnhub (optional, can use env var FINNHUB_API_KEY)
        """
        self.primary_source = primary_source.lower()
        self.fallback_source = fallback_source.lower()
        self.finnhub_api_key = finnhub_api_key or os.environ.get('FINNHUB_API_KEY')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_stock_data(self, symbol, exchange='NSE', days=30):
        """
        Fetch stock data using primary source with fallback
        
        Args:
            symbol: Stock symbol (e.g., 'HDFCBANK')
            exchange: Exchange code (e.g., 'NSE', 'BSE')
            days: Number of days of historical data
            
        Returns:
            pandas.DataFrame with stock data
        """
        print(f"Fetching {symbol} from {self.primary_source.upper()}...")
        
        # Try primary source
        data = self._fetch_from_source(self.primary_source, symbol, exchange, days)
        
        # If primary fails, try fallback
        if data is None or data.empty:
            print(f"  Primary source failed, trying {self.fallback_source.upper()}...")
            data = self._fetch_from_source(self.fallback_source, symbol, exchange, days)
        
        if data is None or data.empty:
            print(f"  ⚠️ Both sources failed for {symbol}")
            return None
        
        print(f"  ✓ Successfully fetched {len(data)} days of data")
        return data
    
    def _fetch_from_source(self, source, symbol, exchange, days):
        """Helper method to fetch from specified source"""
        if source == 'google':
            return self._fetch_from_google(symbol, exchange, days)
        elif source == 'yahoo':
            return self._fetch_from_yahoo(symbol, exchange, days)
        elif source == 'finnhub':
            return self._fetch_from_finnhub(symbol, exchange, days)
        else:
            print(f"  Unknown source: {source}")
            return None
    
    def _fetch_from_google(self, symbol, exchange, days):
        """
        Fetch stock data from Google Finance via web scraping
        
        Note: Google Finance doesn't provide extensive historical data via web scraping.
        This method fetches current price and basic info.
        For historical data, Yahoo Finance is more reliable.
        """
        try:
            # Google Finance URL format
            url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract current price
            price_element = soup.find('div', {'class': 'YMlKec fxKbKc'})
            if not price_element:
                print(f"  Could not find price element for {symbol}")
                return None
            
            current_price = float(price_element.text.replace('₹', '').replace(',', '').strip())
            
            # Extract additional data
            data_dict = {
                'Date': [datetime.now().strftime('%Y-%m-%d')],
                'Symbol': [symbol],
                'Close': [current_price],
                'Open': [current_price],  # Approximation
                'High': [current_price],  # Approximation
                'Low': [current_price],   # Approximation
                'Volume': [0],  # Not available from basic scraping
                'Source': ['Google Finance']
            }
            
            # Try to extract change percentage
            try:
                change_element = soup.find('div', {'class': 'JwB6zf'})
                if change_element:
                    change_text = change_element.text
                    # Extract percentage
                    match = re.search(r'([-+]?\d+\.?\d*)%', change_text)
                    if match:
                        change_pct = float(match.group(1))
                        data_dict['Change_Pct'] = [change_pct]
            except:
                pass
            
            df = pd.DataFrame(data_dict)
            
            # For historical data, we need to use a different approach
            # Google Finance web interface doesn't easily expose historical data
            # So we'll return current data only
            print(f"  Note: Google Finance scraping provides current data only")
            print(f"  For historical data, Yahoo Finance is recommended")
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching from Google Finance: {e}")
            return None
        except Exception as e:
            print(f"  Error parsing Google Finance data: {e}")
            return None
    
    def _fetch_from_yahoo(self, symbol, exchange, days):
        """
        Fetch stock data from Yahoo Finance API
        """
        try:
            # For Indian stocks, add exchange suffix
            if exchange.upper() == 'NSE':
                yahoo_symbol = f"{symbol}.NS"
            elif exchange.upper() == 'BSE':
                yahoo_symbol = f"{symbol}.BO"
            else:
                yahoo_symbol = symbol
            
            # Fetch data for requested period plus buffer for indicators
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 60)  # Extra days for indicator calculation
            
            # Download stock data
            stock = yf.Ticker(yahoo_symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                print(f"  No data found for {yahoo_symbol}")
                return None
            
            # Keep only requested days
            df = df.tail(days).copy()
            
            # Prepare dataframe
            df = df.reset_index()
            df['Symbol'] = symbol
            df['Source'] = 'Yahoo Finance'
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            return df
            
        except Exception as e:
            print(f"  Error fetching from Yahoo Finance: {e}")
            return None
    
    def _fetch_from_finnhub(self, symbol, exchange, days):
        """
        Fetch stock data from Finnhub API
        
        Finnhub provides excellent stock data with free tier support.
        For Indian stocks, we need to use the correct symbol format.
        """
        if not self.finnhub_api_key:
            print(f"  ⚠️ Finnhub API key not configured")
            print(f"  Set FINNHUB_API_KEY environment variable or pass to constructor")
            return None
        
        try:
            # For Indian stocks on NSE, Finnhub uses format: SYMBOL (no suffix)
            # For US stocks, use the symbol as-is
            # Finnhub supports: NSE (India), BSE (India), US exchanges, etc.
            
            # Determine the correct exchange code for Finnhub
            if exchange.upper() == 'NSE':
                finnhub_exchange = 'NS'  # NSE India
                finnhub_symbol = f'{symbol}.{finnhub_exchange}'
            elif exchange.upper() == 'BSE':
                finnhub_exchange = 'BO'  # BSE India
                finnhub_symbol = f'{symbol}.{finnhub_exchange}'
            else:
                finnhub_symbol = symbol
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 60)  # Extra for indicators
            
            # Convert to Unix timestamps
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            # Finnhub API endpoint for stock candles (OHLCV data)
            url = 'https://finnhub.io/api/v1/stock/candle'
            params = {
                'symbol': finnhub_symbol,
                'resolution': 'D',  # Daily resolution
                'from': start_timestamp,
                'to': end_timestamp,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if data is valid
            if data.get('s') != 'ok' or not data.get('c'):
                print(f"  No data available from Finnhub for {finnhub_symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['t'], unit='s'),
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c'],
                'Volume': data['v'],
                'Symbol': symbol,
                'Source': 'Finnhub'
            })
            
            # Keep only requested days
            df = df.tail(days).copy()
            
            # Format date
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df = df.reset_index(drop=True)
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching from Finnhub API: {e}")
            return None
        except Exception as e:
            print(f"  Error parsing Finnhub data: {e}")
            return None
    
    def fetch_multiple_stocks(self, stocks_list, exchange='NSE', days=30):
        """
        Fetch data for multiple stocks
        
        Args:
            stocks_list: List of tuples [(symbol, name), ...]
            exchange: Exchange code
            days: Number of days
            
        Returns:
            Dictionary {symbol: dataframe}
        """
        results = {}
        
        for symbol, name in stocks_list:
            print(f"\n{'='*60}")
            print(f"Processing: {name} ({symbol})")
            print('='*60)
            
            data = self.fetch_stock_data(symbol, exchange, days)
            if data is not None and not data.empty:
                results[symbol] = {
                    'name': name,
                    'data': data
                }
            else:
                print(f"  ⚠️ Skipping {symbol} - no data available")
            
            # Be nice to servers
            time.sleep(1)
        
        return results
    
    def get_current_price(self, symbol, exchange='NSE'):
        """
        Get current price quickly (Google Finance preferred for real-time)
        """
        try:
            url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
            response = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            price_element = soup.find('div', {'class': 'YMlKec fxKbKc'})
            if price_element:
                price = float(price_element.text.replace('₹', '').replace(',', '').strip())
                return price
        except:
            pass
        
        # Fallback to Yahoo
        try:
            yahoo_symbol = f"{symbol}.NS"
            stock = yf.Ticker(yahoo_symbol)
            info = stock.info
            return info.get('currentPrice', info.get('regularMarketPrice', None))
        except:
            return None


class DataSourceConfig:
    """
    Configuration manager for data sources
    """
    
    def __init__(self, config_file='data_source_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            default_config = {
                'primary_source': 'yahoo',
                'fallback_source': 'finnhub',
                'exchange': 'NSE',
                'days': 30,
                'use_cache': True,
                'cache_duration_hours': 1,
                'finnhub_api_key': None
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        self.config = config
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        self.config.update(kwargs)
        self.save_config(self.config)
    
    def get_fetcher(self):
        """Get configured data fetcher instance"""
        return DataFetcher(
            primary_source=self.config.get('primary_source', 'yahoo'),
            fallback_source=self.config.get('fallback_source', 'finnhub'),
            finnhub_api_key=self.config.get('finnhub_api_key')
        )


# Example usage
if __name__ == "__main__":
    # Example 1: Using Yahoo Finance as primary with Finnhub fallback
    print("Example 1: Yahoo Finance Primary, Finnhub Fallback")
    print("="*60)
    fetcher = DataFetcher(primary_source='yahoo', fallback_source='finnhub')
    data = fetcher.fetch_stock_data('HDFCBANK', 'NSE', days=30)
    if data is not None:
        print(f"\nData shape: {data.shape}")
        print(f"\nFirst few rows:")
        print(data.head())
    
    print("\n\n")
    
    # Example 2: Using Finnhub as primary (requires API key)
    print("Example 2: Finnhub Primary, Yahoo Fallback")
    print("="*60)
    print("Note: Set FINNHUB_API_KEY environment variable to use Finnhub")
    fetcher = DataFetcher(primary_source='finnhub', fallback_source='yahoo')
    data = fetcher.fetch_stock_data('RELIANCE', 'NSE', days=30)
    if data is not None:
        print(f"\nData shape: {data.shape}")
        print(f"\nFirst few rows:")
        print(data.head())
    
    print("\n\n")
    
    # Example 3: Using Google Finance with Yahoo fallback
    print("Example 3: Google Finance Primary, Yahoo Fallback")
    print("="*60)
    fetcher = DataFetcher(primary_source='google', fallback_source='yahoo')
    data = fetcher.fetch_stock_data('INFY', 'NSE', days=30)
    if data is not None:
        print(f"\nData shape: {data.shape}")
        print(f"\nFirst few rows:")
        print(data.head())
    
    print("\n\n")
    
    # Example 4: Using configuration
    print("Example 4: Using Configuration Manager")
    print("="*60)
    config = DataSourceConfig()
    print(f"Current config: {json.dumps(config.config, indent=2)}")
    
    fetcher = config.get_fetcher()
    price = fetcher.get_current_price('ITC', 'NSE')
    print(f"\nCurrent price of ITC: ₹{price}")

# Made with Bob - Enhanced with Finnhub Integration
