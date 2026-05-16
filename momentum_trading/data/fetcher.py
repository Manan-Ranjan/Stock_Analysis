"""
Unified Data Fetcher
Integrates NSEpy, Yahoo Finance, Finnhub, and Google Finance
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time

# Import existing data fetcher
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from data_fetcher import DataFetcher as LegacyDataFetcher
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

try:
    from .nse_fetcher import NSEDataFetcher
    NSE_AVAILABLE = True
except ImportError:
    NSE_AVAILABLE = False


class DataFetcher:
    """
    Unified data fetcher supporting multiple sources:
    - NSEpy (Primary for Indian stocks - includes OI)
    - Yahoo Finance (Fallback)
    - Finnhub (Alternative)
    - Google Finance (Real-time prices)
    """
    
    def __init__(
        self,
        primary_source: str = 'nsepy',
        fallback_source: str = 'yahoo',
        finnhub_api_key: Optional[str] = None
    ):
        """
        Initialize unified data fetcher
        
        Args:
            primary_source: 'nsepy', 'yahoo', 'finnhub', or 'google'
            fallback_source: Fallback source
            finnhub_api_key: Finnhub API key (optional)
        """
        self.primary_source = primary_source.lower()
        self.fallback_source = fallback_source.lower()
        
        # Initialize NSE fetcher
        if NSE_AVAILABLE:
            self.nse_fetcher = NSEDataFetcher()
        else:
            self.nse_fetcher = None
            if self.primary_source == 'nsepy':
                print("⚠️ NSEpy not available, switching to Yahoo Finance")
                self.primary_source = 'yahoo'
        
        # Initialize legacy fetcher for Yahoo/Finnhub/Google
        if LEGACY_AVAILABLE:
            self.legacy_fetcher = LegacyDataFetcher(
                primary_source=self.primary_source if self.primary_source != 'nsepy' else 'yahoo',
                fallback_source=self.fallback_source,
                finnhub_api_key=finnhub_api_key
            )
        else:
            self.legacy_fetcher = None
    
    def fetch_stock_data(
        self,
        symbol: str,
        exchange: str = 'NSE',
        days: int = 90,
        include_oi: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data with automatic source selection
        
        Args:
            symbol: Stock symbol
            exchange: Exchange (NSE, BSE)
            days: Number of days
            include_oi: Include Open Interest data (futures)
            
        Returns:
            DataFrame with stock data
        """
        print(f"Fetching {symbol} from {self.primary_source.upper()}...")
        
        # Try primary source
        data = self._fetch_from_source(
            self.primary_source,
            symbol,
            exchange,
            days,
            include_oi
        )
        
        # If primary fails, try fallback
        if data is None or data.empty:
            print(f"  Primary source failed, trying {self.fallback_source.upper()}...")
            data = self._fetch_from_source(
                self.fallback_source,
                symbol,
                exchange,
                days,
                include_oi
            )
        
        if data is None or data.empty:
            print(f"  ⚠️ Both sources failed for {symbol}")
            return None
        
        print(f"  ✓ Successfully fetched {len(data)} days of data")
        return data
    
    def _fetch_from_source(
        self,
        source: str,
        symbol: str,
        exchange: str,
        days: int,
        include_oi: bool
    ) -> Optional[pd.DataFrame]:
        """Fetch from specified source"""
        
        if source == 'nsepy' and self.nse_fetcher:
            return self._fetch_from_nsepy(symbol, days, include_oi)
        
        elif source in ['yahoo', 'finnhub', 'google'] and self.legacy_fetcher:
            return self.legacy_fetcher.fetch_stock_data(symbol, exchange, days)
        
        else:
            print(f"  Source {source} not available")
            return None
    
    def _fetch_from_nsepy(
        self,
        symbol: str,
        days: int,
        include_oi: bool
    ) -> Optional[pd.DataFrame]:
        """Fetch from NSEpy"""
        try:
            if include_oi:
                # Fetch futures data with OI
                return self.nse_fetcher.fetch_futures_data(symbol, days=days)
            else:
                # Fetch regular stock data
                return self.nse_fetcher.fetch_stock_data(symbol, days=days)
        except Exception as e:
            print(f"  Error fetching from NSEpy: {e}")
            return None
    
    def fetch_with_open_interest(
        self,
        symbol: str,
        days: int = 90
    ) -> Optional[pd.DataFrame]:
        """
        Fetch futures data with Open Interest
        Only available through NSEpy
        
        Args:
            symbol: Stock symbol
            days: Number of days
            
        Returns:
            DataFrame with OI data
        """
        if not self.nse_fetcher:
            print("⚠️ Open Interest data requires NSEpy")
            return None
        
        return self.nse_fetcher.fetch_futures_data(symbol, days=days)
    
    def fetch_index_data(
        self,
        index_name: str,
        days: int = 90
    ) -> Optional[pd.DataFrame]:
        """
        Fetch index data (NIFTY, BANKNIFTY, etc.)
        
        Args:
            index_name: Index name
            days: Number of days
            
        Returns:
            DataFrame with index data
        """
        if self.nse_fetcher:
            return self.nse_fetcher.fetch_index_data(index_name, days=days)
        elif self.legacy_fetcher:
            # Try Yahoo Finance for index
            return self.legacy_fetcher.fetch_stock_data(f'^{index_name}', 'NSE', days)
        else:
            return None
    
    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        exchange: str = 'NSE',
        days: int = 90,
        include_oi: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange
            days: Number of days
            include_oi: Include Open Interest
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        for symbol in symbols:
            print(f"\n{'='*60}")
            print(f"Processing: {symbol}")
            print('='*60)
            
            data = self.fetch_stock_data(
                symbol=symbol,
                exchange=exchange,
                days=days,
                include_oi=include_oi
            )
            
            if data is not None and not data.empty:
                results[symbol] = data
            else:
                print(f"  ⚠️ Skipping {symbol} - no data available")
            
            # Be nice to servers
            time.sleep(1)
        
        return results
    
    def get_oi_analysis(self, symbol: str) -> Dict:
        """
        Get Open Interest analysis
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with OI analysis
        """
        if not self.nse_fetcher:
            print("⚠️ OI analysis requires NSEpy")
            return {}
        
        return self.nse_fetcher.get_oi_analysis(symbol)
    
    def get_current_price(
        self,
        symbol: str,
        exchange: str = 'NSE'
    ) -> Optional[float]:
        """
        Get current price quickly
        
        Args:
            symbol: Stock symbol
            exchange: Exchange
            
        Returns:
            Current price
        """
        if self.legacy_fetcher:
            return self.legacy_fetcher.get_current_price(symbol, exchange)
        elif self.nse_fetcher:
            # Get latest price from NSE
            data = self.nse_fetcher.fetch_stock_data(symbol, days=1)
            if data is not None and not data.empty:
                return data['Close'].iloc[-1]
        
        return None


# Example usage
if __name__ == "__main__":
    print("="*60)
    print("Unified Data Fetcher Examples")
    print("="*60)
    
    # Example 1: Fetch with NSEpy (includes deliverable volume)
    print("\n" + "="*60)
    print("Example 1: Fetch Stock Data (NSEpy Primary)")
    print("="*60)
    fetcher = DataFetcher(primary_source='nsepy', fallback_source='yahoo')
    data = fetcher.fetch_stock_data('HDFCBANK', days=30)
    if data is not None:
        print(f"\nData shape: {data.shape}")
        print(f"\nColumns: {data.columns.tolist()}")
        print(f"\nFirst few rows:")
        print(data.head())
    
    # Example 2: Fetch with Open Interest
    print("\n" + "="*60)
    print("Example 2: Fetch Futures Data with Open Interest")
    print("="*60)
    oi_data = fetcher.fetch_with_open_interest('RELIANCE', days=30)
    if oi_data is not None:
        print(f"\nData shape: {oi_data.shape}")
        if 'OI' in oi_data.columns:
            print(f"\nOpen Interest data available!")
            print(f"\nLatest OI data:")
            print(oi_data[['Date', 'Close', 'OI', 'OI_Change', 'OI_Change_Pct']].tail())
    
    # Example 3: OI Analysis
    print("\n" + "="*60)
    print("Example 3: Open Interest Analysis")
    print("="*60)
    oi_analysis = fetcher.get_oi_analysis('RELIANCE')
    if oi_analysis:
        print(f"\nOI Analysis:")
        for key, value in oi_analysis.items():
            print(f"  {key}: {value}")
    
    # Example 4: Fetch Index Data
    print("\n" + "="*60)
    print("Example 4: Fetch Index Data (NIFTY)")
    print("="*60)
    index_data = fetcher.fetch_index_data('NIFTY', days=30)
    if index_data is not None:
        print(f"\nData shape: {index_data.shape}")
        print(f"\nFirst few rows:")
        print(index_data.head())
    
    # Example 5: Multiple stocks
    print("\n" + "="*60)
    print("Example 5: Fetch Multiple Stocks")
    print("="*60)
    stocks = ['HDFCBANK', 'RELIANCE', 'INFY']
    multi_data = fetcher.fetch_multiple_stocks(stocks, days=30)
    print(f"\nFetched data for {len(multi_data)} stocks")
    for symbol, df in multi_data.items():
        print(f"  {symbol}: {len(df)} days")

# Made with Bob
