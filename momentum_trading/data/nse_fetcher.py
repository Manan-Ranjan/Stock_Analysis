"""
NSE Data Fetcher using NSEpy
Specialized fetcher for Indian stock market data with Open Interest support
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import time

try:
    from nsepy import get_history
    from nsepy.derivatives import get_expiry_date
    NSEPY_AVAILABLE = True
except ImportError:
    NSEPY_AVAILABLE = False
    print("Warning: nsepy not installed. Install with: pip install nsepy")


class NSEDataFetcher:
    """
    Fetch data from NSE India using NSEpy library
    Supports stocks, indices, futures, and options with Open Interest
    """
    
    def __init__(self):
        """Initialize NSE data fetcher"""
        if not NSEPY_AVAILABLE:
            raise ImportError("nsepy is required. Install with: pip install nsepy")
        
        self.cache = {}
        self.cache_duration = 3600  # 1 hour in seconds
    
    def fetch_stock_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 90,
        index: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock/index data from NSE
        
        Args:
            symbol: Stock symbol (e.g., 'HDFCBANK', 'RELIANCE')
            start_date: Start date for historical data
            end_date: End date for historical data
            days: Number of days if start_date not provided
            index: True if fetching index data (e.g., 'NIFTY', 'BANKNIFTY')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Set date range
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=days)
            
            print(f"Fetching {symbol} from NSE ({start_date.date()} to {end_date.date()})...")
            
            # Fetch data using nsepy
            df = get_history(
                symbol=symbol,
                start=start_date,
                end=end_date,
                index=index
            )
            
            if df is None or df.empty:
                print(f"  ⚠️ No data found for {symbol}")
                return None
            
            # Standardize column names
            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'Date',
                'Symbol': 'Symbol',
                'Open': 'Open',
                'High': 'High',
                'Low': 'Low',
                'Close': 'Close',
                'Last': 'Last',
                'Volume': 'Volume',
                'Turnover': 'Turnover',
                'Trades': 'Trades',
                'Deliverable Volume': 'Deliverable_Volume',
                '%Deliverble': 'Deliverable_Pct'
            })
            
            # Add metadata
            df['Symbol'] = symbol
            df['Source'] = 'NSE (nsepy)'
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            
            print(f"  ✓ Successfully fetched {len(df)} days of data")
            return df
            
        except Exception as e:
            print(f"  ❌ Error fetching {symbol} from NSE: {e}")
            return None
    
    def fetch_futures_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 90,
        expiry_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch futures data with Open Interest
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            days: Number of days
            expiry_date: Futures expiry date (auto-detected if None)
            
        Returns:
            DataFrame with futures data including Open Interest
        """
        try:
            # Set date range
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=days)
            
            # Get expiry date if not provided
            if expiry_date is None:
                expiry_date = get_expiry_date(year=end_date.year, month=end_date.month)
            
            print(f"Fetching {symbol} futures (Expiry: {expiry_date.date()})...")
            
            # Fetch futures data
            df = get_history(
                symbol=symbol,
                start=start_date,
                end=end_date,
                futures=True,
                expiry_date=expiry_date
            )
            
            if df is None or df.empty:
                print(f"  ⚠️ No futures data found for {symbol}")
                return None
            
            # Standardize columns
            df = df.reset_index()
            df['Symbol'] = symbol
            df['Source'] = 'NSE Futures (nsepy)'
            df['Expiry'] = expiry_date.strftime('%Y-%m-%d')
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            
            # Open Interest is available in 'Open Interest' column
            if 'Open Interest' in df.columns:
                df['OI'] = df['Open Interest']
                df['OI_Change'] = df['OI'].diff()
                df['OI_Change_Pct'] = df['OI'].pct_change() * 100
            
            print(f"  ✓ Successfully fetched {len(df)} days of futures data")
            return df
            
        except Exception as e:
            print(f"  ❌ Error fetching futures data for {symbol}: {e}")
            return None
    
    def fetch_options_data(
        self,
        symbol: str,
        strike_price: float,
        option_type: str = 'CE',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 30,
        expiry_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch options data with Open Interest
        
        Args:
            symbol: Stock symbol
            strike_price: Strike price
            option_type: 'CE' for Call or 'PE' for Put
            start_date: Start date
            end_date: End date
            days: Number of days
            expiry_date: Options expiry date
            
        Returns:
            DataFrame with options data including Open Interest
        """
        try:
            # Set date range
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=days)
            
            # Get expiry date if not provided
            if expiry_date is None:
                expiry_date = get_expiry_date(year=end_date.year, month=end_date.month)
            
            print(f"Fetching {symbol} {strike_price} {option_type} options...")
            
            # Fetch options data
            df = get_history(
                symbol=symbol,
                start=start_date,
                end=end_date,
                option_type=option_type,
                strike_price=strike_price,
                expiry_date=expiry_date
            )
            
            if df is None or df.empty:
                print(f"  ⚠️ No options data found")
                return None
            
            # Standardize columns
            df = df.reset_index()
            df['Symbol'] = symbol
            df['Strike'] = strike_price
            df['Option_Type'] = option_type
            df['Source'] = 'NSE Options (nsepy)'
            df['Expiry'] = expiry_date.strftime('%Y-%m-%d')
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            
            # Open Interest analysis
            if 'Open Interest' in df.columns:
                df['OI'] = df['Open Interest']
                df['OI_Change'] = df['OI'].diff()
                df['OI_Change_Pct'] = df['OI'].pct_change() * 100
            
            print(f"  ✓ Successfully fetched {len(df)} days of options data")
            return df
            
        except Exception as e:
            print(f"  ❌ Error fetching options data: {e}")
            return None
    
    def fetch_index_data(
        self,
        index_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 90
    ) -> Optional[pd.DataFrame]:
        """
        Fetch index data (NIFTY, BANKNIFTY, etc.)
        
        Args:
            index_name: Index name ('NIFTY', 'BANKNIFTY', 'NIFTY IT', etc.)
            start_date: Start date
            end_date: End date
            days: Number of days
            
        Returns:
            DataFrame with index data
        """
        return self.fetch_stock_data(
            symbol=index_name,
            start_date=start_date,
            end_date=end_date,
            days=days,
            index=True
        )
    
    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        days: int = 90,
        delay: float = 1.0
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            days: Number of days
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        for symbol in symbols:
            data = self.fetch_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                days=days
            )
            
            if data is not None and not data.empty:
                results[symbol] = data
            
            # Be nice to the server
            time.sleep(delay)
        
        return results
    
    def get_oi_analysis(
        self,
        symbol: str,
        expiry_date: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        Get Open Interest analysis for futures
        
        Args:
            symbol: Stock symbol
            expiry_date: Expiry date
            
        Returns:
            Dictionary with OI analysis
        """
        try:
            # Fetch recent futures data
            df = self.fetch_futures_data(
                symbol=symbol,
                days=30,
                expiry_date=expiry_date
            )
            
            if df is None or df.empty or 'OI' not in df.columns:
                return {}
            
            # Calculate OI metrics
            latest_oi = df['OI'].iloc[-1]
            oi_change = df['OI_Change'].iloc[-1] if 'OI_Change' in df.columns else 0
            oi_change_pct = df['OI_Change_Pct'].iloc[-1] if 'OI_Change_Pct' in df.columns else 0
            
            # Price change
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0
            price_change_pct = (price_change / df['Close'].iloc[-2] * 100) if len(df) > 1 else 0
            
            # OI interpretation
            interpretation = self._interpret_oi(price_change_pct, oi_change_pct)
            
            return {
                'symbol': symbol,
                'latest_oi': latest_oi,
                'oi_change': oi_change,
                'oi_change_pct': oi_change_pct,
                'price_change_pct': price_change_pct,
                'interpretation': interpretation,
                'signal': interpretation['signal']
            }
            
        except Exception as e:
            print(f"Error in OI analysis: {e}")
            return {}
    
    def _interpret_oi(self, price_change_pct: float, oi_change_pct: float) -> Dict[str, str]:
        """
        Interpret Open Interest changes with price movements
        
        Rules:
        - Price ↑ + OI ↑ = Long Build-up (Bullish)
        - Price ↓ + OI ↑ = Short Build-up (Bearish)
        - Price ↑ + OI ↓ = Short Covering (Bullish)
        - Price ↓ + OI ↓ = Long Unwinding (Bearish)
        """
        if price_change_pct > 0 and oi_change_pct > 0:
            return {
                'signal': 'Bullish',
                'type': 'Long Build-up',
                'description': 'Price rising with increasing OI - Fresh long positions'
            }
        elif price_change_pct < 0 and oi_change_pct > 0:
            return {
                'signal': 'Bearish',
                'type': 'Short Build-up',
                'description': 'Price falling with increasing OI - Fresh short positions'
            }
        elif price_change_pct > 0 and oi_change_pct < 0:
            return {
                'signal': 'Bullish',
                'type': 'Short Covering',
                'description': 'Price rising with decreasing OI - Shorts covering positions'
            }
        elif price_change_pct < 0 and oi_change_pct < 0:
            return {
                'signal': 'Bearish',
                'type': 'Long Unwinding',
                'description': 'Price falling with decreasing OI - Longs exiting positions'
            }
        else:
            return {
                'signal': 'Neutral',
                'type': 'No Clear Trend',
                'description': 'Mixed signals or minimal changes'
            }


# Example usage
if __name__ == "__main__":
    if NSEPY_AVAILABLE:
        fetcher = NSEDataFetcher()
        
        # Example 1: Fetch stock data
        print("\n" + "="*60)
        print("Example 1: Fetch Stock Data")
        print("="*60)
        stock_data = fetcher.fetch_stock_data('HDFCBANK', days=30)
        if stock_data is not None:
            print(f"\nData shape: {stock_data.shape}")
            print(f"\nColumns: {stock_data.columns.tolist()}")
            print(f"\nFirst few rows:")
            print(stock_data.head())
        
        # Example 2: Fetch futures data with OI
        print("\n" + "="*60)
        print("Example 2: Fetch Futures Data with Open Interest")
        print("="*60)
        futures_data = fetcher.fetch_futures_data('RELIANCE', days=30)
        if futures_data is not None:
            print(f"\nData shape: {futures_data.shape}")
            if 'OI' in futures_data.columns:
                print(f"\nOpen Interest columns: OI, OI_Change, OI_Change_Pct")
                print(f"\nLatest OI data:")
                print(futures_data[['Date', 'Close', 'OI', 'OI_Change', 'OI_Change_Pct']].tail())
        
        # Example 3: OI Analysis
        print("\n" + "="*60)
        print("Example 3: Open Interest Analysis")
        print("="*60)
        oi_analysis = fetcher.get_oi_analysis('RELIANCE')
        if oi_analysis:
            print(f"\nOI Analysis for RELIANCE:")
            for key, value in oi_analysis.items():
                print(f"  {key}: {value}")
    else:
        print("Please install nsepy: pip install nsepy")

# Made with Bob
